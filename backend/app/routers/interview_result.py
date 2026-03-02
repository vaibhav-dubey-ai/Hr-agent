"""Interview result submission endpoint - interview outcome & conditional Q&A generation."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from app.schemas import InterviewResultRequest, InterviewResultResponse
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["interview"])


@router.post("/interview-result", response_model=InterviewResultResponse)
async def submit_interview_result(request: InterviewResultRequest):
    """
    Submit interview result: candidate selected or rejected.
    
    Business Logic:
    - If selected: transition to offer_extended and generate interview questions
    - If rejected: transition to rejected (no questions)
    
    Request body:
    {
        "candidate_id": "candidate_0",
        "decision": "selected" | "rejected",
        "reason": "Excellent technical skills and cultural fit" | "Does not meet technical requirements"
    }
    
    Response if SELECTED:
    {
        "status": "success",
        "new_state": "offer_extended",
        "questions_generated": true,
        "technical_questions": [...],
        "behavioral_questions": [...],
        "timestamp": "2026-03-01T..."
    }
    
    Response if REJECTED:
    {
        "status": "success",
        "new_state": "rejected",
        "questions_generated": false,
        "rejection_reason": "Does not meet technical requirements",
        "timestamp": "2026-03-01T..."
    }
    """
    try:
        # Validate input
        if not request.candidate_id or not request.candidate_id.strip():
            return InterviewResultResponse(
                status="error",
                new_state="unknown",
                questions_generated=False,
                error_code="INVALID_CANDIDATE_ID",
                message="Candidate ID is required and cannot be empty",
                timestamp=datetime.now()
            )
        
        if request.decision not in ["selected", "rejected"]:
            return InterviewResultResponse(
                status="error",
                new_state="unknown",
                questions_generated=False,
                error_code="INVALID_DECISION",
                message="Decision must be 'selected' or 'rejected'",
                timestamp=datetime.now()
            )
        
        if not request.reason or not request.reason.strip():
            return InterviewResultResponse(
                status="error",
                new_state="unknown",
                questions_generated=False,
                error_code="INVALID_REASON",
                message="Reason is required",
                timestamp=datetime.now()
            )
        
        agent = get_hr_agent()
        
        # Get current candidate state
        current_state_dict = agent.get_candidate_state(request.candidate_id)
        if not current_state_dict or not current_state_dict.get("candidate_id"):
            return InterviewResultResponse(
                status="error",
                new_state="unknown",
                questions_generated=False,
                error_code="CANDIDATE_NOT_FOUND",
                message=f"Candidate {request.candidate_id} not found in pipeline",
                timestamp=datetime.now()
            )
        
        current_state = current_state_dict.get("current_state")
        
        # Verify candidate is in interviewed state (before decision)
        # Allow from any non-terminal state for flexibility, but ideal is "interviewed"
        if current_state in ["hired", "rejected"]:
            return InterviewResultResponse(
                status="error",
                new_state=current_state,
                questions_generated=False,
                error_code="INVALID_STATE_TRANSITION",
                message=f"Cannot submit interview result for candidate in terminal state '{current_state}'",
                timestamp=datetime.now()
            )
        
        # ===== DECISION: SELECTED =====
        if request.decision == "selected":
            # STRICT: Only allow from "interviewed" state
            if current_state != "interviewed":
                return InterviewResultResponse(
                    status="error",
                    new_state=current_state,
                    questions_generated=False,
                    error_code="INVALID_STATE_TRANSITION",
                    message=f"Candidate must be in 'interviewed' state to submit selection decision, currently in '{current_state}'",
                    timestamp=datetime.now()
                )
            
            # Transition to offer_extended (with deterministic question generation)
            success, error_msg = agent.advance_candidate_state(
                request.candidate_id,
                "offer_extended",
                f"Interview result: selected - {request.reason}"
            )
            
            if not success:
                return InterviewResultResponse(
                    status="error",
                    new_state=current_state,
                    questions_generated=False,
                    error_code="STATE_TRANSITION_FAILED",
                    message=error_msg or "Failed to transition to offer_extended",
                    timestamp=datetime.now()
                )
            
            # Generate interview questions for offer package
            # Use reason as JD context for deterministic question generation
            try:
                questions_dict = agent.generate_interview_questions(
                    jd_text=request.reason,  # Use reason as JD context
                    resume_text="",
                    num_technical=6,
                    num_behavioral=4
                )
                
                technical_qs = questions_dict.get("technical", [])
                behavioral_qs = questions_dict.get("behavioral", [])
                
                return InterviewResultResponse(
                    status="success",
                    new_state="offer_extended",
                    questions_generated=True,
                    technical_questions=technical_qs,
                    behavioral_questions=behavioral_qs,
                    timestamp=datetime.now()
                )
            
            except Exception as e:
                # Questions generation failed, but state transition succeeded
                # Return success with questions_generated=false to indicate partial success
                return InterviewResultResponse(
                    status="success",
                    new_state="offer_extended",
                    questions_generated=False,
                    message=f"Transitioned to offer_extended, but question generation failed: {str(e)}",
                    timestamp=datetime.now()
                )
        
        # ===== DECISION: REJECTED =====
        else:  # decision == "rejected"
            # Transition to rejected (allowed from any non-terminal state)
            success, error_msg = agent.advance_candidate_state(
                request.candidate_id,
                "rejected",
                request.reason
            )
            
            if not success:
                return InterviewResultResponse(
                    status="error",
                    new_state=current_state,
                    questions_generated=False,
                    error_code="STATE_TRANSITION_FAILED",
                    message=error_msg or f"Failed to transition to rejected state",
                    timestamp=datetime.now()
                )
            
            # Return rejection response (no questions)
            return InterviewResultResponse(
                status="success",
                new_state="rejected",
                questions_generated=False,
                rejection_reason=request.reason,
                timestamp=datetime.now()
            )
    
    except Exception as e:
        return InterviewResultResponse(
            status="error",
            new_state="unknown",
            questions_generated=False,
            error_code="INTERNAL_ERROR",
            message=f"Server error: {str(e)}",
            timestamp=datetime.now()
        )
