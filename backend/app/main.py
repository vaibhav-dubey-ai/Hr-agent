"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

from app.config import settings
from app.schemas import HealthResponse
from app.routers import ranking, leave, scheduling, pipeline, questions, export, interview_result

# Startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    # Startup
    print("✓ Starting HR Agent API...")
    try:
        from app.core.hr_agent import get_hr_agent
        agent = get_hr_agent()
        print(f"✓ Loaded HR Agent with 1200 resumes and 300 leave records")
    except Exception as e:
        print(f"✗ Failed to load HR Agent: {e}")
    
    yield
    
    # Shutdown
    print("✓ Shutting down HR Agent API...")

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Production-grade HR Automation API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ranking.router)
app.include_router(leave.router)
app.include_router(scheduling.router)
app.include_router(pipeline.router)
app.include_router(questions.router)
app.include_router(interview_result.router)
app.include_router(export.router)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION
    )

# Root endpoint
@app.get("/")
async def root():
    """API root."""
    return {
        "message": "HR Agent API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler."""
    return {
        "error": str(exc.detail),
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
