from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import httpx
import logging

from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify service status and dependencies.
    """
    health_status = {
        "status": "healthy",
        "version": settings.api_version,
        "environment": settings.environment,
        "services": {
            "api": "operational",
            "supabase": "unknown",
            "gemini": "unknown"
        }
    }
    
    # Check Supabase connectivity (non-blocking)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/rest/v1/",
                timeout=5.0
            )
            if response.status_code < 500:
                health_status["services"]["supabase"] = "operational"
            else:
                health_status["services"]["supabase"] = "degraded"
    except Exception as e:
        logger.warning(f"Supabase health check failed: {e}")
        health_status["services"]["supabase"] = "unreachable"
    
    # Check if Gemini API key is configured
    if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
        health_status["services"]["gemini"] = "configured"
    else:
        health_status["services"]["gemini"] = "not_configured"
    
    # Determine overall health
    if health_status["services"]["supabase"] == "unreachable":
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, bool]:
    """
    Readiness check to determine if the service is ready to accept traffic.
    """
    is_ready = True
    
    # Check if required environment variables are set
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        is_ready = False
    
    if not settings.supabase_url or not settings.supabase_anon_key:
        is_ready = False
    
    if not is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"ready": is_ready}