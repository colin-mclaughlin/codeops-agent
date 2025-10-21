from backend.app.utils.logging import get_logger


class GitTool:
    """Stub Git tool for simulating branch operations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def run(self, branch: str = "sandbox") -> dict:
        """
        Stub Git tool: simulate branch operations.
        
        Args:
            branch: Branch name to checkout
            
        Returns:
            Dictionary containing tool execution results
        """
        self.logger.info(f"GitTool: checked out branch {branch}")
        return {"tool": "git", "branch": branch, "status": "ok"}
