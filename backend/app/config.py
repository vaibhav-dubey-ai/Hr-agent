"""Configuration for FastAPI backend."""

import os
from typing import Optional

class Settings:
    """Application settings from environment variables."""
    
    # API
    API_TITLE: str = "HR Agent API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Data paths
    RESUME_CSV: str = os.getenv("RESUME_CSV", "resume_dataset_1200.csv")
    LEAVE_EXCEL: str = os.getenv("LEAVE_EXCEL", "employee leave tracking data.xlsx")
    
    # Pagination
    DEFAULT_TOP_K: int = 20
    
settings = Settings()
