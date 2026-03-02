"""Interview question generation endpoint."""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import QuestionGenerationRequest, QuestionResponse
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["questions"])

@router.post("/generate-questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """
    Generate interview questions based on JD and candidate profile.
    
    - **jd_text**: Job description
    - **candidate_name**: Candidate name (optional)
    - **candidate_background**: Candidate resume/background (optional)
    """
    try:
        agent = get_hr_agent()
        
        if not request.jd_text or len(request.jd_text.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters")
        
        # Generate questions
        questions_dict = agent.generate_interview_questions(
            jd_text=request.jd_text,
            resume_text=request.candidate_background
        )
        
        return QuestionResponse(
            technical_questions=questions_dict.get("technical", []),
            behavioral_questions=questions_dict.get("behavioral", []),
            scoring_guide=questions_dict.get("scoring_guide", {}),
            timestamp=datetime.now()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")
