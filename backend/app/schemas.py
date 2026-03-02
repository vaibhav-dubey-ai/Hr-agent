"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# RANKING ENDPOINTS
# ============================================================================

class RankRequest(BaseModel):
    """Resume ranking request."""
    jd_text: str = Field(..., description="Job description text")
    top_k: int = Field(20, ge=1, le=100, description="Number of candidates to return")

class ScoreBreakdown(BaseModel):
    """Score component breakdown for rubric compliance."""
    skills_match_score: float
    experience_score: float
    education_score: float
    certification_score: float
    final_score: float
    normalized_score: float

class CandidateRanking(BaseModel):
    """Single ranked candidate with score breakdown."""
    rank: int
    candidate_id: str  # e.g. "candidate_0"
    name: str
    score: float
    normalized_score: float
    score_breakdown: ScoreBreakdown
    reasoning: Dict[str, Any]
    target_job: str

class RankResponse(BaseModel):
    """Resume ranking response."""
    candidates: List[CandidateRanking]
    total_candidates: int
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# LEAVE ENDPOINTS
# ============================================================================

class LeaveRequest(BaseModel):
    """Leave approval request."""
    employee_name: str = Field(..., description="Employee name")
    leave_type: str = Field(..., description="Type of leave (Casual, Sick, Annual, Maternity)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    days_requested: int = Field(..., ge=1, description="Number of days")

class LeaveDecision(BaseModel):
    """Leave approval decision with formal evidence."""
    employee_name: str
    leave_type: str
    start_date: str
    end_date: str
    days_requested: int
    decision_type: str  # "approved" or "rejected"
    applied_policy_rules: List[str]
    evidence: Dict[str, Any]

class LeaveResponse(BaseModel):
    """Leave request response."""
    decision: LeaveDecision
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# SCHEDULING ENDPOINTS
# ============================================================================

class InterviewScheduleRequest(BaseModel):
    """Interview scheduling request."""
    candidate_id: str = Field(..., description="Candidate ID")
    interviewer_id: str = Field(..., description="Interviewer ID")
    preferred_date: str = Field(..., description="Preferred date (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="Preferred time (HH:MM)")

class ScheduleResult(BaseModel):
    """Scheduling result with error codes and conflict details."""
    candidate_id: str
    interviewer_id: str
    status: str  # "success" or "failed"
    error_code: Optional[str] = None
    error_message: str
    conflict_details: Optional[Dict[str, Any]] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None

class ScheduleResponse(BaseModel):
    """Scheduling response."""
    schedule: ScheduleResult
    timestamp: datetime = Field(default_factory=datetime.now)

class InterviewerAvailabilityRequest(BaseModel):
    """Register interviewer availability."""
    interviewer_id: str = Field(..., description="Interviewer ID")
    available_dates: List[str] = Field(..., description="List of available dates (YYYY-MM-DD)")
    available_times: List[str] = Field(..., description="List of available times (HH:MM)")

# ============================================================================
# PIPELINE ENDPOINTS
# ============================================================================

class PipelineTransitionRequest(BaseModel):
    """Candidate state transition request."""
    candidate_id: str = Field(..., description="Candidate ID")
    new_state: str = Field(..., description="New state (applied, screened, interviewed, etc.)")
    reason: str = Field(default="", description="Reason for transition")

class PipelineStateModel(BaseModel):
    """Candidate pipeline state."""
    candidate_id: str
    current_state: str
    is_terminal: bool
    allowed_transitions: List[str]
    history: List[Dict[str, Any]]

class PipelineResponse(BaseModel):
    """Pipeline transition response with allowed transitions."""
    success: bool
    message: str
    candidate_id: str
    current_state: str
    allowed_next_states: List[str]
    is_terminal: bool
    history: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# INTERVIEW QUESTIONS
# ============================================================================

class QuestionGenerationRequest(BaseModel):
    """Interview question generation request."""
    jd_text: str = Field(..., description="Job description")
    candidate_name: str = Field(default="", description="Candidate name")
    candidate_background: str = Field(default="", description="Candidate background/resume")

class ScoringGuide(BaseModel):
    """Scoring rubric for evaluating answers."""
    category: str
    levels: Dict[str, str]

class QuestionResponse(BaseModel):
    """Generated interview questions."""
    technical_questions: List[str]
    behavioral_questions: List[str]
    scoring_guide: Dict[str, Dict[str, str]]
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# EXPORT
# ============================================================================

class ExportResponse(BaseModel):
    """Complete system state export."""
    rankings: List[Dict[str, Any]]
    leave_decisions: List[Dict[str, Any]]
    pipeline_history: List[Dict[str, Any]]
    interview_schedules: List[Dict[str, Any]]
    interview_questions: List[Dict[str, Any]]

# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationError(BaseModel):
    """Validation error response."""
    error: str
    fields: Dict[str, List[str]]
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# INTERVIEW RESULT (NEW)
# ============================================================================

class InterviewResultRequest(BaseModel):
    """Interview result submission (selection or rejection)."""
    candidate_id: str = Field(..., description="Candidate ID")
    decision: str = Field(..., description="Decision: 'selected' or 'rejected'")
    reason: str = Field(..., description="Reason for decision")

class InterviewResultResponse(BaseModel):
    """Response when candidate is selected - includes generated questions."""
    status: str = Field(..., description="'success' or 'error'")
    new_state: str = Field(..., description="New pipeline state")
    questions_generated: bool = Field(..., description="Whether questions were generated")
    technical_questions: Optional[List[str]] = Field(None, description="Technical interview questions")
    behavioral_questions: Optional[List[str]] = Field(None, description="Behavioral interview questions")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    message: Optional[str] = Field(None, description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.now)

class StandardResponse(BaseModel):
    """Standard response format for all endpoints."""
    status: str = Field(..., description="'success' or 'error'")
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
