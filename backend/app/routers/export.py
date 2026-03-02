"""Export endpoint."""

from fastapi import APIRouter, HTTPException
import json

from app.schemas import ExportResponse
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["export"])

@router.get("/export", response_model=dict)
async def export_results():
    """
    Export all results as JSON.
    
    Returns complete state of rankings, leave decisions, schedules, and pipeline.
    """
    try:
        agent = get_hr_agent()
        json_str = agent.export_results()
        
        # Parse and return as dict
        return json.loads(json_str)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
