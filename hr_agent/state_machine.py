from enum import Enum
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class PipelineState(Enum):
    """Defines valid pipeline states."""
    APPLIED = "applied"
    SCREENED = "screened"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    HIRED = "hired"
    REJECTED = "rejected"

class StateMachine:
    """Finite State Machine for candidate pipeline - Strict enforcement."""
    
    # Define valid transitions in strict order
    # Pipeline sequence: applied → screened → interview_scheduled → interviewed → offer_extended → offer_accepted → hired
    # Rejection allowed from any non-terminal state
    VALID_TRANSITIONS = {
        PipelineState.APPLIED: [
            PipelineState.SCREENED,
            PipelineState.REJECTED
        ],
        PipelineState.SCREENED: [
            PipelineState.INTERVIEW_SCHEDULED,
            PipelineState.REJECTED
        ],
        PipelineState.INTERVIEW_SCHEDULED: [
            PipelineState.INTERVIEWED,
            PipelineState.REJECTED
        ],
        PipelineState.INTERVIEWED: [
            PipelineState.OFFER_EXTENDED,
            PipelineState.REJECTED
        ],
        PipelineState.OFFER_EXTENDED: [
            PipelineState.OFFER_ACCEPTED,
            PipelineState.REJECTED
        ],
        PipelineState.OFFER_ACCEPTED: [
            PipelineState.HIRED,
            PipelineState.REJECTED
        ],
        PipelineState.HIRED: [],  # Terminal - no transitions
        PipelineState.REJECTED: []  # Terminal - no transitions
    }
    
    # Define state order for sequence validation
    STATE_SEQUENCE = [
        PipelineState.APPLIED,
        PipelineState.SCREENED,
        PipelineState.INTERVIEW_SCHEDULED,
        PipelineState.INTERVIEWED,
        PipelineState.OFFER_EXTENDED,
        PipelineState.OFFER_ACCEPTED,
        PipelineState.HIRED
    ]
    
    def __init__(self, candidate_id: str):
        self.candidate_id = candidate_id
        self.current_state = PipelineState.APPLIED
        self.history: List[Dict] = [
            {
                "state": self.current_state.value,
                "timestamp": datetime.now().isoformat(),
                "action": "initialized"
            }
        ]
    
    def transition(self, new_state: PipelineState, reason: str = "") -> Tuple[bool, Optional[str], List[str]]:
        """
        Attempt to transition to a new state with strict validation.
        
        Returns:
            Tuple[bool, Optional[str], List[str]]: (success, error_message, allowed_next_states)
        """
        # Validate state is valid enum
        if isinstance(new_state, str):
            try:
                new_state = PipelineState(new_state)
            except ValueError:
                allowed = [s.value for s in self.VALID_TRANSITIONS[self.current_state]]
                return False, f"Invalid state: {new_state}", allowed
        
        # Check if new_state is in valid transitions
        if new_state not in self.VALID_TRANSITIONS[self.current_state]:
            allowed = [s.value for s in self.VALID_TRANSITIONS[self.current_state]]
            error_msg = f"Cannot transition from {self.current_state.value} to {new_state.value}"
            return False, error_msg, allowed
        
        # Prevent duplicate states (no staying in same state)
        if new_state == self.current_state:
            allowed = [s.value for s in self.VALID_TRANSITIONS[self.current_state]]
            return False, f"Already in state {self.current_state.value}", allowed
        
        # Update state and history
        self.current_state = new_state
        self.history.append({
            "state": new_state.value,
            "timestamp": datetime.now().isoformat(),
            "reason": reason if reason else ""
        })
        
        # Return allowed next states
        next_allowed = [s.value for s in self.VALID_TRANSITIONS[new_state]]
        return True, None, next_allowed
    
    def get_current_state(self) -> str:
        """Get current state as string."""
        return self.current_state.value
    
    def get_history(self) -> List[Dict]:
        """Get full transition history."""
        return self.history
    
    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (no further transitions possible)."""
        return len(self.VALID_TRANSITIONS[self.current_state]) == 0
    
    def can_transition_to(self, target_state: PipelineState) -> bool:
        """Check if transition to target_state is valid."""
        return target_state in self.VALID_TRANSITIONS[self.current_state]
    
    def get_allowed_transitions(self) -> List[str]:
        """Get list of allowed next states."""
        return [s.value for s in self.VALID_TRANSITIONS[self.current_state]]
    
    def to_dict(self) -> Dict:
        """Export state machine to dictionary."""
        return {
            "candidate_id": self.candidate_id,
            "current_state": self.current_state.value,
            "is_terminal": self.is_terminal_state(),
            "allowed_transitions": self.get_allowed_transitions(),
            "history": self.history
        }
