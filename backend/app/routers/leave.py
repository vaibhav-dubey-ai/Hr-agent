"""Leave management endpoint."""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import LeaveRequest, LeaveResponse, LeaveDecision, ErrorResponse
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["leave"])

@router.post("/leave", response_model=LeaveResponse)
async def process_leave_request(request: LeaveRequest):
    """
    Process a leave request with policy compliance.
    
    - **employee_name**: Employee name
    - **leave_type**: Type (Casual, Sick, Annual, Maternity)
    - **start_date**: YYYY-MM-DD
    - **end_date**: YYYY-MM-DD
    - **days_requested**: Number of days
    """
    try:
        agent = get_hr_agent()
        
        # Validate dates format
        try:
            from datetime import datetime as dt
            dt.strptime(request.start_date, "%Y-%m-%d")
            dt.strptime(request.end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Process leave
        decision_dict = agent.process_leave_request(
            employee_name=request.employee_name,
            leave_type=request.leave_type,
            start_date=request.start_date,
            end_date=request.end_date,
            days_requested=request.days_requested
        )
        
        # Convert to response
        decision = LeaveDecision(
            employee_name=decision_dict["employee_name"],
            leave_type=decision_dict.get("leave_type", request.leave_type),
            start_date=decision_dict.get("start_date", request.start_date),
            end_date=decision_dict.get("end_date", request.end_date),
            days_requested=decision_dict.get("days_requested", request.days_requested),
            decision_type=decision_dict["decision_type"],
            applied_policy_rules=decision_dict.get("applied_policy_rules", []),
            evidence=decision_dict.get("evidence", {})
        )
        
        return LeaveResponse(
            decision=decision,
            timestamp=datetime.now()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leave processing failed: {str(e)}")
