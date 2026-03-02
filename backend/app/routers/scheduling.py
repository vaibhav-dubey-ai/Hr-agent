"""Interview scheduling endpoint."""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import InterviewScheduleRequest, InterviewerAvailabilityRequest, ScheduleResponse, ScheduleResult
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["scheduling"])

@router.post("/schedule/availability")
async def register_availability(request: InterviewerAvailabilityRequest):
    """
    Register interviewer availability.
    
    - **interviewer_id**: Unique interviewer ID
    - **available_dates**: List of dates (YYYY-MM-DD)
    - **available_times**: List of times (HH:MM)
    """
    try:
        agent = get_hr_agent()
        agent.register_interviewer_availability(
            request.interviewer_id,
            request.available_dates,
            request.available_times
        )
        
        return {
            "status": "success",
            "message": f"Registered {len(request.available_dates)} dates for {request.interviewer_id}",
            "timestamp": datetime.now()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_interview(request: InterviewScheduleRequest):
    """
    Schedule an interview with conflict detection.
    
    - **candidate_id**: Candidate ID
    - **interviewer_id**: Interviewer ID
    - **preferred_date**: Date (YYYY-MM-DD)
    - **preferred_time**: Time (HH:MM)
    """
    try:
        agent = get_hr_agent()
        
        # Validate date/time format
        try:
            from datetime import datetime as dt
            dt.strptime(request.preferred_date, "%Y-%m-%d")
            dt.strptime(request.preferred_time, "%H:%M")
        except ValueError:
            raise ValueError("Invalid date/time format")
        
        # Schedule interview
        schedule_dict = agent.schedule_interview(
            candidate_id=request.candidate_id,
            interviewer_id=request.interviewer_id,
            preferred_date=request.preferred_date,
            preferred_time=request.preferred_time
        )
        
        # Convert response
        schedule = ScheduleResult(
            candidate_id=schedule_dict["candidate_id"],
            interviewer_id=schedule_dict["interviewer_id"],
            status=schedule_dict["status"],
            error_code=schedule_dict.get("error_code"),
            error_message=schedule_dict.get("error_message", ""),
            conflict_details=schedule_dict.get("conflict_details"),
            scheduled_date=schedule_dict.get("scheduled_date"),
            scheduled_time=schedule_dict.get("scheduled_time")
        )
        
        return ScheduleResponse(
            schedule=schedule,
            timestamp=datetime.now()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")
