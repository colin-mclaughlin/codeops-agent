from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from backend.app.agent.slack_tool import SlackTool
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/slack", tags=["slack"])
logger = get_logger(__name__)


class SummaryRequest(BaseModel):
    verdict: str
    repo: str
    run_log_id: int = None
    pr_url: str = None


class PRNotificationRequest(BaseModel):
    action: str
    repo: str
    pr_number: int
    pr_url: str
    title: str = None


class ErrorNotificationRequest(BaseModel):
    error: str
    context: str = None


@router.get("/test")
def send_test_message(msg: str = Query("Hello from CodeOps Agent")):
    """
    Send a test message to Slack.
    
    Args:
        msg: Message to send (default: "Hello from CodeOps Agent")
        
    Returns:
        Dictionary with success status and any error details
    """
    try:
        slack = SlackTool()
        result = slack.post_message(msg)
        logger.info(f"Test message sent to Slack: {msg}")
        return result
    except Exception as e:
        logger.error(f"Error sending test message to Slack: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/summary")
def send_run_summary(request: SummaryRequest):
    """
    Send a run summary to Slack.
    
    Args:
        request: SummaryRequest with verdict, repo, and optional fields
        
    Returns:
        Dictionary with success status and any error details
    """
    try:
        slack = SlackTool()
        result = slack.post_summary(request.verdict, request.repo, request.pr_url, request.run_log_id)
        logger.info(f"Run summary sent to Slack for {request.repo}: {request.verdict}")
        return result
    except Exception as e:
        logger.error(f"Error sending run summary to Slack: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pr-notification")
def send_pr_notification(request: PRNotificationRequest):
    """
    Send a PR notification to Slack.
    
    Args:
        request: PRNotificationRequest with action, repo, pr_number, pr_url, and optional title
        
    Returns:
        Dictionary with success status and any error details
    """
    try:
        slack = SlackTool()
        result = slack.post_pr_notification(request.action, request.repo, request.pr_number, request.pr_url, request.title)
        logger.info(f"PR notification sent to Slack: {request.action} for {request.repo}#{request.pr_number}")
        return result
    except Exception as e:
        logger.error(f"Error sending PR notification to Slack: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/error")
def send_error_notification(request: ErrorNotificationRequest):
    """
    Send an error notification to Slack.
    
    Args:
        request: ErrorNotificationRequest with error and optional context
        
    Returns:
        Dictionary with success status and any error details
    """
    try:
        slack = SlackTool()
        result = slack.post_error_notification(request.error, request.context)
        logger.info(f"Error notification sent to Slack: {request.error}")
        return result
    except Exception as e:
        logger.error(f"Error sending error notification to Slack: {e}")
        raise HTTPException(status_code=400, detail=str(e))
