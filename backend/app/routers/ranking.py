"""Resume ranking endpoint."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from app.schemas import RankRequest, RankResponse, CandidateRanking, ErrorResponse
from app.core.hr_agent import get_hr_agent

router = APIRouter(prefix="/api", tags=["ranking"])

@router.post("/rank", response_model=RankResponse)
async def rank_resumes(request: RankRequest):
    """
    Rank resumes against a job description.
    
    - **jd_text**: Job description text
    - **top_k**: Number of candidates to return (1-100)
    """
    try:
        agent = get_hr_agent()
        
        if not request.jd_text or len(request.jd_text.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters")
        
        # Get rankings from agent
        rankings = agent.rank_resumes(request.jd_text, top_k=request.top_k)
        
        # Convert to response format
        candidates = [
            CandidateRanking(**ranking)
            for ranking in rankings
        ]
        
        return RankResponse(
            candidates=candidates,
            total_candidates=len(candidates),
            timestamp=datetime.now()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")
