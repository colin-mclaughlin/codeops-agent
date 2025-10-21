from backend.app.utils.logging import get_logger


class NotifierTool:
    """Stub notifier tool for simulating notifications (e.g., Slack/Discord)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def run(self, message: str = "Pipeline finished") -> dict:
        """
        Stub notifier (e.g., Slack/Discord).
        
        Args:
            message: Message to send
            
        Returns:
            Dictionary containing tool execution results
        """
        self.logger.info(f"NotifierTool: sent notification '{message}'")
        return {"tool": "notifier", "message": message, "status": "ok"}
