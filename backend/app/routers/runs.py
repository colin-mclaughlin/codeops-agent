from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from backend.app.db import get_session
from backend.app.models.run_log import RunLog
from backend.app.agent.reasoning import AgentRun
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])
logger = get_logger(__name__)


@router.get("/runs")
async def get_agent_runs(
    limit: int = 50,
    session: AsyncSession = Depends(get_session)
) -> List[dict]:
    """
    Get recent agent runs with their associated run logs.
    
    Args:
        limit: Maximum number of runs to return (default: 50)
        session: Database session
        
    Returns:
        List of agent runs with metadata
    """
    try:
        # Query agent runs with optional run log join
        stmt = (
            select(AgentRun)
            .order_by(desc(AgentRun.created_at))
            .limit(limit)
        )
        
        result = await session.execute(stmt)
        agent_runs = result.scalars().all()
        
        runs_data = []
        for run in agent_runs:
            # Get associated run log if it exists
            run_log = None
            if run.run_log_id:
                stmt_log = select(RunLog).where(RunLog.id == run.run_log_id)
                result_log = await session.execute(stmt_log)
                run_log = result_log.scalar_one_or_none()
            
            # Calculate latency and tokens (mock values for now)
            latency_ms = 1000 + (run.id * 50)  # Mock latency
            tokens_used = len(run.plan.split()) * 10  # Mock token count
            
            # Determine verdict from result
            verdict = "success" if run.result.get("status") == "ok" else "failure"
            
            run_data = {
                "id": run.id,
                "run_log_id": run.run_log_id,
                "timestamp": run.created_at.isoformat() + "Z",
                "verdict": verdict,
                "plan": run.plan,
                "status": run.result.get("status", "unknown"),
                "latency_ms": latency_ms,
                "tokens_used": tokens_used
            }
            
            # Add run log event type if available
            if run_log:
                run_data["event_type"] = run_log.event_type
            
            runs_data.append(run_data)
        
        logger.info(f"Retrieved {len(runs_data)} agent runs")
        return runs_data
        
    except Exception as e:
        logger.error(f"Error retrieving agent runs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent runs")


@router.get("/runs/{run_id}")
async def get_agent_run(
    run_id: int,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Get a specific agent run by ID.
    
    Args:
        run_id: ID of the agent run
        session: Database session
        
    Returns:
        Agent run details
    """
    try:
        stmt = select(AgentRun).where(AgentRun.id == run_id)
        result = await session.execute(stmt)
        agent_run = result.scalar_one_or_none()
        
        if not agent_run:
            raise HTTPException(status_code=404, detail="Agent run not found")
        
        # Get associated run log if it exists
        run_log = None
        if agent_run.run_log_id:
            stmt_log = select(RunLog).where(RunLog.id == agent_run.run_log_id)
            result_log = await session.execute(stmt_log)
            run_log = result_log.scalar_one_or_none()
        
        # Calculate metadata
        latency_ms = 1000 + (agent_run.id * 50)
        tokens_used = len(agent_run.plan.split()) * 10
        verdict = "success" if agent_run.result.get("status") == "ok" else "failure"
        
        run_data = {
            "id": agent_run.id,
            "run_log_id": agent_run.run_log_id,
            "timestamp": agent_run.created_at.isoformat() + "Z",
            "verdict": verdict,
            "plan": agent_run.plan,
            "status": agent_run.result.get("status", "unknown"),
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "result": agent_run.result
        }
        
        if run_log:
            run_data["run_log"] = {
                "id": run_log.id,
                "event_type": run_log.event_type,
                "payload": run_log.payload,
                "created_at": run_log.created_at.isoformat() + "Z"
            }
        
        return run_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent run {run_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent run")
