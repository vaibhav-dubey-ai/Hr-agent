"""Global response wrapper and error handling middleware."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class GlobalResponseWrapper:
    """Middleware to wrap all responses in standard format."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # For HTTP requests, wrap the response
        async def send_with_wrapper(message):
            if message["type"] == "http.response.start":
                # Let the response proceed normally
                await send(message)
            elif message["type"] == "http.response.body":
                # Body is sent as-is
                await send(message)
        
        await self.app(scope, receive, send_with_wrapper)

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

def wrap_response(data: dict = None, status: str = "success", error_code: str = None, message: str = None) -> dict:
    """
    Create a standard response wrapper.
    
    Args:
        data: The response data
        status: "success" or "error"
        error_code: Error code if status is "error"
        message: Human-readable message
    
    Returns:
        Standard response dictionary
    """
    return {
        "status": status,
        "data": data,
        "error_code": error_code,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
