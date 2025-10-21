from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db import get_session
from backend.app.agent.reasoning import AgentOrchestrator
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])
logger = get_logger(__name__)


@router.post("/run/{run_log_id}")
async def run_agent(run_log_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Trigger the agent pipeline for a specific RunLog.
    Returns the pipeline plan and result summary.
    
    Args:
        run_log_id: ID of the RunLog to process
        session: Database session
        
    Returns:
        Dictionary containing pipeline execution summary
    """
    agent = AgentOrchestrator(session)
    logger.info(f"Agent run initiated for RunLog {run_log_id}")
    result = await agent.run_pipeline(run_log_id)
    logger.info(f"Agent run completed for RunLog {run_log_id}")
    return result
