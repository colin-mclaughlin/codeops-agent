from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from backend.app.agent.critic_agent import CriticAgent
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/critic", tags=["critic"])
logger = get_logger(__name__)


class CritiqueRequest(BaseModel):
    plan: str
    reflection: str
    context: str = ""


class QuickReviewRequest(BaseModel):
    plan: str


@router.post("/review")
async def review_output(request: CritiqueRequest):
    """
    Review primary agent's plan and reflection.
    
    Args:
        request: CritiqueRequest with plan, reflection, and optional context
        
    Returns:
        Dictionary containing critique results
    """
    try:
        critic = CriticAgent()
        result = await critic.critique(request.plan, request.reflection, request.context)
        logger.info(f"Critic review completed with confidence: {result.get('confidence', 0)}")
        return result
    except Exception as e:
        logger.error(f"Error performing critic review: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/quick-review")
async def quick_review(request: QuickReviewRequest):
    """
    Perform a quick review of just the plan.
    
    Args:
        request: QuickReviewRequest with plan
        
    Returns:
        Dictionary containing quick review results
    """
    try:
        critic = CriticAgent()
        result = await critic.quick_review(request.plan)
        logger.info(f"Quick review completed with confidence: {result.get('confidence', 0)}")
        return result
    except Exception as e:
        logger.error(f"Error performing quick review: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/summary")
async def get_critique_summary(request: CritiqueRequest):
    """
    Get a formatted summary of a critique for display.
    
    Args:
        request: CritiqueRequest with plan, reflection, and optional context
        
    Returns:
        Dictionary containing formatted summary
    """
    try:
        critic = CriticAgent()
        critique_result = await critic.critique(request.plan, request.reflection, request.context)
        summary = critic.get_critique_summary(critique_result)
        
        return {
            "summary": summary,
            "confidence": critique_result.get("confidence", 0),
            "timestamp": critique_result.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Error generating critique summary: {e}")
        raise HTTPException(status_code=400, detail=str(e))
