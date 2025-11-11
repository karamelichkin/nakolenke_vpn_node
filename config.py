"""
Configuration and logging setup for VPN daemon.
"""
import os
import logging
import sys
from typing import Optional, List
from dotenv import load_dotenv


VPN_L2TP = 0
VPN_IKEV2 = 1
VPN_SOCKS5 = 2
VPN_HTTP = 3
VPN_WHATSAPP = 4
VPN_WIREGUARD = 5
VPN_AMNEZIA = 6

VPN_TYPE_MAP = {
    'l2tp': VPN_L2TP,
    'ikev2': VPN_IKEV2,
    'socks5': VPN_SOCKS5,
    'http': VPN_HTTP,
    'whatsapp': VPN_WHATSAPP,
    'wireguard': VPN_WIREGUARD,
    'amnezia': VPN_AMNEZIA,
}

VPN_TYPE_NAMES = {v: k for k, v in VPN_TYPE_MAP.items()}

class Config:
    """Application configuration loaded from environment variables."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.listen_host: str = os.getenv('LISTEN_HOST', '0.0.0.0')
        self.listen_port: int = int(os.getenv('LISTEN_PORT', '8080'))
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO').upper()

        # Supported VPN types from config
        supported_vpns_str = os.getenv('SUPPORTED_VPN_TYPES', 'wireguard,ikev2')
        vpn_names = [vpn.strip() for vpn in supported_vpns_str.split(',')]
        self.supported_vpn_types: List[int] = []

        for vpn_name in vpn_names:
            if vpn_name in VPN_TYPE_MAP:
                self.supported_vpn_types.append(VPN_TYPE_MAP[vpn_name])
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if not (1 <= self.listen_port <= 65535):
            raise ValueError(f"Invalid port number: {self.listen_port}")
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")

def setup_logging(level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, logs to stdout.
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create handler
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    handler.setLevel(numeric_level)
    handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Set specific loggers to appropriate levels
    # Reduce uvicorn noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    if level.upper() not in ['DEBUG']:
        logging.getLogger("uvicorn").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module."""
    return logging.getLogger(name)

# Global config instance
config = Config()
