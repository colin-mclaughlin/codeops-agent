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


@router.get("/github-context")
async def get_github_context(repo: str = "octocat/Hello-World", session: AsyncSession = Depends(get_session)) -> dict:
    """
    Test GitHub integration by fetching repository context.
    
    Args:
        repo: GitHub repository in format "username/repo-name"
        session: Database session
        
    Returns:
        Dictionary containing GitHub context data
    """
    agent = AgentOrchestrator(session)
    logger.info(f"Fetching GitHub context for repository: {repo}")
    result = await agent.github_actions(repo)
    logger.info(f"GitHub context retrieved for repository: {repo}")
    return result


@router.get("/langgraph")
async def run_langgraph(commit_sha: str = "latest", repo: str = "octocat/Hello-World", session: AsyncSession = Depends(get_session)) -> dict:
    """
    Run LangGraph-style reasoning pipeline for advanced decision-making.
    
    Args:
        commit_sha: Commit SHA for context retrieval (default: "latest")
        repo: GitHub repository in format "username/repo-name"
        session: Database session
        
    Returns:
        Dictionary containing LangGraph pipeline results
    """
    agent = AgentOrchestrator(session)
    logger.info(f"Running LangGraph reasoning for commit {commit_sha} in repository: {repo}")
    result = await agent.run_langgraph(commit_sha, repo)
    logger.info(f"LangGraph reasoning completed for repository: {repo}")
    return result