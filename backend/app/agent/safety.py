from backend.app.utils.logging import get_logger

logger = get_logger(__name__)

# Safety configuration
MAX_TOKENS = 20000
ALLOWED_TOOLS = {"git", "test_runner", "notifier"}


def check_permissions(tool_name: str) -> bool:
    """
    Return True if tool is allowed, else log a warning and return False.
    
    Args:
        tool_name: Name of the tool to check
        
    Returns:
        True if tool is allowed, False otherwise
    """
    if tool_name not in ALLOWED_TOOLS:
        logger.warning(f"Permission denied for tool '{tool_name}'")
        return False
    return True


def within_token_budget(tokens_used: int) -> bool:
    """
    Return True if within token budget.
    
    Args:
        tokens_used: Number of tokens consumed
        
    Returns:
        True if within budget, False otherwise
    """
    if tokens_used > MAX_TOKENS:
        logger.warning(f"Token limit exceeded: {tokens_used}/{MAX_TOKENS}")
        return False
    return True
