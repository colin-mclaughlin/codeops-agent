import os
import requests
from datetime import datetime
from backend.app.utils.logging import get_logger
from backend.app.config import settings

logger = get_logger(__name__)


class SlackTool:
    """
    MCP tool for posting CodeOps Agent notifications to Slack.
    """

    def __init__(self):
        """
        Initialize SlackTool with webhook URL from settings.
        """
        self.webhook = settings.SLACK_WEBHOOK_URL
        if not self.webhook:
            raise ValueError("SLACK_WEBHOOK_URL not configured in .env")
        logger.info("SlackTool initialized successfully")

    def post_message(self, text: str, emoji: str = ":robot_face:"):
        """
        Send a basic text message to Slack.
        
        Args:
            text: Message text to send
            emoji: Emoji to prefix the message (default: robot_face)
            
        Returns:
            Dictionary with success status and any error details
        """
        try:
            payload = {
                "text": f"{emoji} {text}\n_Time: {datetime.utcnow().isoformat()}Z_"
            }
            response = requests.post(self.webhook, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Slack post failed: {response.text}")
                return {"ok": False, "error": response.text, "status_code": response.status_code}
            
            logger.info(f"Slack message sent: {text[:50]}...")
            return {"ok": True, "message": text[:50]}
            
        except Exception as e:
            logger.error(f"Slack post error: {e}")
            return {"ok": False, "error": str(e)}

    def post_summary(self, verdict: str, repo: str, pr_url: str = None, run_log_id: int = None):
        """
        Send a structured run summary (used after agent run or PR creation).
        
        Args:
            verdict: Run verdict ("success" or "failure")
            repo: Repository name
            pr_url: Optional pull request URL
            run_log_id: Optional run log ID
            
        Returns:
            Dictionary with success status and any error details
        """
        try:
            color = ":green_heart:" if verdict == "success" else ":x:"
            message = f"{color} *CodeOps Agent Run Summary*\n• Repository: {repo}\n• Verdict: {verdict}"
            
            if run_log_id:
                message += f"\n• Run ID: {run_log_id}"
            
            if pr_url:
                message += f"\n• Pull Request: <{pr_url}|View on GitHub>"
            
            return self.post_message(message, emoji=":gear:")
            
        except Exception as e:
            logger.error(f"Slack summary post error: {e}")
            return {"ok": False, "error": str(e)}

    def post_pr_notification(self, action: str, repo: str, pr_number: int, pr_url: str, title: str = None):
        """
        Send a notification about PR actions (created, updated, etc.).
        
        Args:
            action: Action performed ("created", "updated", "merged", etc.)
            repo: Repository name
            pr_number: Pull request number
            pr_url: Pull request URL
            title: Optional PR title
            
        Returns:
            Dictionary with success status and any error details
        """
        try:
            emoji_map = {
                "created": ":new:",
                "updated": ":arrows_counterclockwise:",
                "merged": ":white_check_mark:",
                "closed": ":x:"
            }
            emoji = emoji_map.get(action, ":gear:")
            
            message = f"{emoji} *Pull Request {action.title()}*\n• Repository: {repo}\n• PR #{pr_number}"
            
            if title:
                message += f"\n• Title: {title}"
            
            message += f"\n• <{pr_url}|View on GitHub>"
            
            return self.post_message(message, emoji=":octocat:")
            
        except Exception as e:
            logger.error(f"Slack PR notification error: {e}")
            return {"ok": False, "error": str(e)}

    def post_error_notification(self, error: str, context: str = None):
        """
        Send an error notification to Slack.
        
        Args:
            error: Error message
            context: Optional context information
            
        Returns:
            Dictionary with success status and any error details
        """
        try:
            message = f":warning: *CodeOps Agent Error*\n• Error: {error}"
            
            if context:
                message += f"\n• Context: {context}"
            
            return self.post_message(message, emoji=":rotating_light:")
            
        except Exception as e:
            logger.error(f"Slack error notification error: {e}")
            return {"ok": False, "error": str(e)}
