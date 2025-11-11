#!/usr/bin/env python3
"""
VPN Daemon - Main application entry point.

A daemon for managing VPN connections on FreeBSD nodes.
Supports L2TP/IPSec, IKEv2, WireGuard, and Amnezia VPN types.
"""
import sys
import signal
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import config, setup_logging, get_logger
from api import router

# Global logger
logger = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("VPN Daemon starting up...")
    logger.info(f"Listening on {config.listen_host}:{config.listen_port}")
    logger.info(f"Log level: {config.log_level}")

    # Инициализация базы данных
    try:
        from storage.database import init_db, engine
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("VPN Daemon shutting down...")

    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    from fastapi import Request, HTTPException
    import ipaddress
    import os

    app = FastAPI(
        title="VPN Daemon",
        description="A daemon for managing VPN connections on FreeBSD nodes",
        version="1.0.0-dev",
        lifespan=lifespan
    )

    # Простая IP фильтрация через middleware
    allowed_ips = os.getenv('VPN_ALLOWED_IPS', '').split(',')
    allowed_ips = [ip.strip() for ip in allowed_ips if ip.strip()]

    if allowed_ips:
        @app.middleware("http")
        async def ip_filter(request: Request, call_next):
            client_ip = request.headers.get("X-Forwarded-For", request.client.host)
            if "," in client_ip:
                client_ip = client_ip.split(",")[0].strip()

            allowed = False
            try:
                for allowed_ip in allowed_ips:
                    if '/' in allowed_ip:  # subnet
                        if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_ip, strict=False):
                            allowed = True
                            break
                    elif client_ip == allowed_ip:
                        allowed = True
                        break
            except:
                pass

            if not allowed:
                raise HTTPException(status_code=403, detail="Access denied")

            return await call_next(request)

    app.include_router(router, prefix="/api/v1")
    return app

def main():
    """Main application entry point."""
    global logger

    try:
        # Validate configuration
        config.validate()

        # Setup logging
        setup_logging(level=config.log_level)
        logger = get_logger(__name__)

        logger.info("VPN Daemon initializing...")
        logger.debug(f"Configuration: host={config.listen_host}, port={config.listen_port}, log_level={config.log_level}")

        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Create application
        app = create_app()

        # Run server
        uvicorn.run(
            app,
            host=config.listen_host,
            port=config.listen_port,
            log_config=None,  # Use our logging config
            access_log=False  # Disable uvicorn access logs, we handle them
        )

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
