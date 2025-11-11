"""
API routes for VPN daemon.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import time
from datetime import datetime

from config import get_logger, config

logger = get_logger(__name__)

router = APIRouter()

class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    status: str
    version: str
    uptime_seconds: float
    timestamp: str


class TypesResponse(BaseModel):
    """Response model for types endpoint."""
    types: List[int]

# Store start time for uptime calculation
start_time = time.time()

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get daemon status information.
    
    Returns:
        StatusResponse: Current daemon status and system information
    """
    try:
        logger.debug("Status endpoint called")
        
        # Calculate uptime
        uptime = time.time() - start_time
        
        response = StatusResponse(
            status="ok",
            version="1.0.0-dev",
            uptime_seconds=round(uptime, 2),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Status request completed. Uptime: {uptime:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/types")
async def get_types():
    try:
        logger.debug("Types endpoint called")
        return TypesResponse(types=config.supported_vpn_types)

    except Exception as e:
        logger.error(f"Error in types endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")