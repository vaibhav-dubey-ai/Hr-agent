"""Candidate pipeline state management endpoint."""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import PipelineTransitionRequest, PipelineResponse, PipelineStateModel
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["pipeline"])

# Valid pipeline order (FSM)
VALID_STATES = [
    "applied",
    "screened",
    "interview_scheduled",
    "interviewed",
    "offer_extended",
    "offer_accepted",
    "hired",
    "rejected"
]

# Define valid transitions (strict FSM enforcement)
VALID_TRANSITIONS = {
    "applied": ["screened", "rejected"],
    "screened": ["interview_scheduled", "rejected"],
    "interview_scheduled": ["interviewed", "rejected"],
    "interviewed": ["offer_extended", "rejected"],
    "offer_extended": ["offer_accepted", "rejected"],
    "offer_accepted": ["hired", "rejected"],
    "hired": [],  # Terminal
    "rejected": []  # Terminal
}

def validate_transition(current_state: str, new_state: str) -> tuple:
    """
    Validate state transition.
    Returns (is_valid, error_message)
    """
    if current_state not in VALID_STATES:
        return False, f"Unknown current state: {current_state}"
    
    if new_state not in VALID_STATES:
        return False, f"Unknown target state: {new_state}"
    
    if new_state not in VALID_TRANSITIONS.get(current_state, []):
        # Build helpful error message
        allowed = VALID_TRANSITIONS.get(current_state, [])
        path_str = " → ".join([current_state] + allowed)
        return False, f"Cannot transition from {current_state} to {new_state}. Allowed: {path_str}"
    
    return True, ""

@router.post("/transition", response_model=PipelineResponse)
async def transition_candidate(request: PipelineTransitionRequest):
    """
    Move candidate to next state in pipeline (STRICT FSM with allowed transitions).
    
    Valid transitions:
    - applied → screened, rejected
    - screened → interview_scheduled, rejected
    - interview_scheduled → interviewed, rejected
    - interviewed → offer_extended, rejected
    - offer_extended → offer_accepted, rejected
    - offer_accepted → hired, rejected
    - hired (terminal) - no further transitions
    - rejected (terminal) - no further transitions
    """
    try:
        # Validate input
        if not request.candidate_id or not request.candidate_id.strip():
            return PipelineResponse(
                success=False,
                message="Candidate ID is required",
                candidate_id=request.candidate_id,
                current_state="unknown",
                allowed_next_states=[],
                is_terminal=False,
                history=[]
            )
        
        agent = get_hr_agent()
        
        # Get current state first
        current_state_dict = agent.get_candidate_state(request.candidate_id)
        if not current_state_dict:
            return PipelineResponse(
                success=False,
                message=f"Candidate {request.candidate_id} not found",
                candidate_id=request.candidate_id,
                current_state="unknown",
                allowed_next_states=[],
                is_terminal=False,
                history=[]
            )
        
        current_state = current_state_dict.get("current_state")
        
        # Attempt transition
        success, error_msg = agent.advance_candidate_state(
            candidate_id=request.candidate_id,
            new_state=request.new_state,
            reason=request.reason
        )
        
        if not success:
            allowed_next = VALID_TRANSITIONS.get(current_state, [])
            return PipelineResponse(
                success=False,
                message=error_msg or f"State transition failed",
                candidate_id=request.candidate_id,
                current_state=current_state,
                allowed_next_states=allowed_next,
                is_terminal=current_state_dict.get("is_terminal", False),
                history=current_state_dict.get("history", [])
            )
        
        # Get updated state
        state_dict = agent.get_candidate_state(request.candidate_id)
        
        return PipelineResponse(
            success=True,
            message=f"Successfully transitioned to {request.new_state}",
            candidate_id=state_dict["candidate_id"],
            current_state=state_dict["current_state"],
            allowed_next_states=state_dict.get("allowed_transitions", []),
            is_terminal=state_dict.get("is_terminal", False),
            history=state_dict.get("history", [])
        )
    
    except Exception as e:
        return PipelineResponse(
            success=False,
            message=f"Internal server error: {str(e)}",
            candidate_id=request.candidate_id,
            current_state="error",
            allowed_next_states=[],
            is_terminal=False,
            history=[]
        )

@router.get("/state/{candidate_id}", response_model=PipelineResponse)
async def get_candidate_state(candidate_id: str):
    """Get current state of a candidate with allowed transitions."""
    try:
        agent = get_hr_agent()
        state_dict = agent.get_candidate_state(candidate_id)
        
        if not state_dict:
            return PipelineResponse(
                success=False,
                message="Candidate not found",
                candidate_id=candidate_id,
                current_state="unknown",
                allowed_next_states=[],
                is_terminal=False,
                history=[]
            )
        
        return PipelineResponse(
            success=True,
            message="State retrieved",
            candidate_id=state_dict["candidate_id"],
            current_state=state_dict["current_state"],
            allowed_next_states=state_dict.get("allowed_transitions", []),
            is_terminal=state_dict.get("is_terminal", False),
            history=state_dict.get("history", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
