from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db import get_session
from backend.app.agent.reasoning import AgentRun
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/metrics", tags=["metrics"])
logger = get_logger(__name__)

# Global counters for metrics
TOTAL_RUNS = 0
SUCCESS_RUNS = 0
CRITIC_RUNS = 0
AVG_CONFIDENCE = 0.0


def record_run(verdict: str) -> None:
    """
    Record a run result in the global metrics counters.
    
    Args:
        verdict: "success" or "failure"
    """
    global TOTAL_RUNS, SUCCESS_RUNS
    TOTAL_RUNS += 1
    if verdict == "success":
        SUCCESS_RUNS += 1


def record_critic(confidence: int) -> None:
    """
    Record a critic run with confidence score.
    
    Args:
        confidence: Confidence score (0-100)
    """
    global CRITIC_RUNS, AVG_CONFIDENCE
    CRITIC_RUNS += 1
    AVG_CONFIDENCE = round(((AVG_CONFIDENCE * (CRITIC_RUNS - 1)) + confidence) / CRITIC_RUNS, 2)
    logger.info(f"Critic run recorded: confidence={confidence}, avg={AVG_CONFIDENCE}")


@router.get("/")
async def get_metrics(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Get system metrics from database.
    
    Returns:
        Dictionary containing current metrics data
    """
    logger.info("metrics endpoint hit")
    
    try:
        # Get all agent runs
        stmt = select(AgentRun)
        result = await session.execute(stmt)
        runs = result.scalars().all()
        
        if not runs:
            return {
                "total_runs": 0,
                "success_rate": 0,
                "avg_latency": 0,
                "avg_tokens": 0,
                "avg_cost_usd": 0,
                "total_tokens": 0,
                "total_cost_usd": 0,
                "critic_runs": CRITIC_RUNS,
                "avg_confidence": AVG_CONFIDENCE
            }
        
        total_runs = len(runs)
        successes = [r for r in runs if r.result.get("status") == "ok"]
        success_rate = (len(successes) / total_runs) * 100 if total_runs > 0 else 0
        
        # Calculate averages
        total_tokens = sum(r.token_count or 0 for r in runs)
        total_cost = sum(r.cost_usd or 0.0 for r in runs)
        avg_tokens = total_tokens / total_runs if total_runs > 0 else 0
        avg_cost = total_cost / total_runs if total_runs > 0 else 0
        
        # Mock latency calculation (you can replace this with actual latency tracking)
        avg_latency = 1300  # This could be calculated from actual execution times
        
        return {
            "total_runs": total_runs,
            "success_rate": round(success_rate, 1),
            "avg_latency": round(avg_latency, 1),
            "avg_tokens": round(avg_tokens, 1),
            "avg_cost_usd": round(avg_cost, 5),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 5),
            "critic_runs": CRITIC_RUNS,
            "avg_confidence": AVG_CONFIDENCE
        }
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        # Return fallback metrics in case of error
        return {
            "total_runs": TOTAL_RUNS,
            "success_rate": round(SUCCESS_RUNS / TOTAL_RUNS, 2) if TOTAL_RUNS else 0,
            "avg_latency": 1300,
            "avg_tokens": 0,
            "avg_cost_usd": 0,
            "total_tokens": 0,
            "total_cost_usd": 0,
            "critic_runs": CRITIC_RUNS,
            "avg_confidence": AVG_CONFIDENCE
        }
