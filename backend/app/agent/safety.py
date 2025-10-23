import os
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)

# Safety configuration
MAX_TOKENS = 20000
ALLOWED_TOOLS = {"git", "test_runner", "notifier", "github"}
BLOCKED_BRANCHES = {"main", "master", "develop", "production"}
BLOCKED_PATHS = {"/etc", "/usr", "/bin", "/sbin", "/var", "/opt"}


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


def is_dry_run_mode() -> bool:
    """
    Check if the agent is running in dry-run mode.
    
    Returns:
        True if in dry-run mode, False otherwise
    """
    return os.getenv("AGENT_DRY_RUN", "false").lower() == "true"


def validate_branch_name(branch_name: str) -> bool:
    """
    Validate that a branch name is safe to use.
    
    Args:
        branch_name: The branch name to validate
        
    Returns:
        True if safe, False otherwise
    """
    if not branch_name:
        logger.warning("Empty branch name provided")
        return False
    
    # Check against blocked branches
    if branch_name.lower() in BLOCKED_BRANCHES:
        logger.warning(f"Blocked branch name: {branch_name}")
        return False
    
    # Ensure agent prefix for safety
    if not branch_name.startswith("agent-fix/"):
        logger.warning(f"Branch name must start with 'agent-fix/': {branch_name}")
        return False
    
    # Check for dangerous characters
    dangerous_chars = ["..", "/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in dangerous_chars:
        if char in branch_name:
            logger.warning(f"Branch name contains dangerous character '{char}': {branch_name}")
            return False
    
    return True


def validate_repo_path(repo_path: str) -> bool:
    """
    Validate that a repository path is safe to use.
    
    Args:
        repo_path: The repository path to validate
        
    Returns:
        True if safe, False otherwise
    """
    if not repo_path:
        logger.warning("Empty repository path provided")
        return False
    
    # Convert to absolute path for checking
    abs_path = os.path.abspath(repo_path)
    
    # Check against blocked paths
    for blocked_path in BLOCKED_PATHS:
        if abs_path.startswith(blocked_path):
            logger.warning(f"Repository path blocked: {abs_path}")
            return False
    
    # Check if path exists and is a directory
    if not os.path.exists(abs_path):
        logger.warning(f"Repository path does not exist: {abs_path}")
        return False
    
    if not os.path.isdir(abs_path):
        logger.warning(f"Repository path is not a directory: {abs_path}")
        return False
    
    return True


def log_operation(operation: str, details: dict) -> None:
    """
    Log a safety-critical operation with details.
    
    Args:
        operation: The operation being performed
        details: Dictionary with operation details
    """
    logger.info(f"SAFETY LOG - {operation}: {details}")


def check_github_token() -> bool:
    """
    Check if GitHub token is available and valid.
    
    Returns:
        True if token is available, False otherwise
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN environment variable not set")
        return False
    
    if len(token) < 10:
        logger.warning("GITHUB_TOKEN appears to be invalid (too short)")
        return False
    
    return True
