from fastapi import APIRouter, HTTPException
from backend.app.agent.github_tool import GitHubTool
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/github", tags=["github"])
logger = get_logger(__name__)


@router.get("/commits")
def get_commits(repo: str, limit: int = 5):
    """
    Get recent commits from a GitHub repository.
    
    Args:
        repo: Repository name in format "username/repo-name"
        limit: Maximum number of commits to return (default: 5)
        
    Returns:
        List of recent commits with sha, message, author, and date
    """
    try:
        gh = GitHubTool(repo)
        commits = gh.list_recent_commits(limit)
        logger.info(f"Retrieved {len(commits)} commits for repository {repo}")
        return {"repository": repo, "commits": commits}
    except Exception as e:
        logger.error(f"Error retrieving commits for {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows")
def get_workflows(repo: str, limit: int = 5):
    """
    Get recent workflow runs from a GitHub repository.
    
    Args:
        repo: Repository name in format "username/repo-name"
        limit: Maximum number of workflow runs to return per workflow (default: 5)
        
    Returns:
        List of recent workflow runs with status, conclusion, and URL
    """
    try:
        gh = GitHubTool(repo)
        workflows = gh.get_workflow_runs(limit)
        logger.info(f"Retrieved {len(workflows)} workflow runs for repository {repo}")
        return {"repository": repo, "workflows": workflows}
    except Exception as e:
        logger.error(f"Error retrieving workflows for {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repo-info")
def get_repository_info(repo: str):
    """
    Get basic information about a GitHub repository.
    
    Args:
        repo: Repository name in format "username/repo-name"
        
    Returns:
        Repository information including name, description, stars, etc.
    """
    try:
        gh = GitHubTool(repo)
        info = gh.get_repository_info()
        logger.info(f"Retrieved repository info for {repo}")
        return info
    except Exception as e:
        logger.error(f"Error retrieving repository info for {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/branch")
def create_branch(repo: str, base: str, new_branch: str):
    """
    Create a new branch from a base branch.
    
    Args:
        repo: Repository name in format "username/repo-name"
        base: Base branch name (e.g., "main")
        new_branch: New branch name
        
    Returns:
        Branch creation details
    """
    try:
        gh = GitHubTool(repo)
        result = gh.create_branch(base, new_branch)
        logger.info(f"Created branch '{new_branch}' from '{base}' in repository {repo}")
        return result
    except Exception as e:
        logger.error(f"Error creating branch in {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/commit")
def commit_file(repo: str, branch: str, file_path: str, content: str, message: str):
    """
    Update a file and commit the changes.
    
    Args:
        repo: Repository name in format "username/repo-name"
        branch: Branch name to commit to
        file_path: Path to the file to update
        content: New content for the file
        message: Commit message
        
    Returns:
        Commit details
    """
    try:
        gh = GitHubTool(repo)
        result = gh.commit_and_push(branch, file_path, content, message)
        logger.info(f"Committed file '{file_path}' to branch '{branch}' in repository {repo}")
        return result
    except Exception as e:
        logger.error(f"Error committing file in {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pull-request")
def create_pull_request(repo: str, title: str, body: str, head: str, base: str = "main"):
    """
    Create a new pull request.
    
    Args:
        repo: Repository name in format "username/repo-name"
        title: PR title
        body: PR description
        head: Source branch name
        base: Target branch name (default: "main")
        
    Returns:
        Pull request details
    """
    try:
        gh = GitHubTool(repo)
        result = gh.open_pull_request(title, body, head, base)
        logger.info(f"Created pull request '{title}' in repository {repo}")
        return result
    except Exception as e:
        logger.error(f"Error creating pull request in {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/comment")
def comment_on_pr(repo: str, pr_number: int, message: str):
    """
    Add a comment to a pull request.
    
    Args:
        repo: Repository name in format "username/repo-name"
        pr_number: Pull request number
        message: Comment message
        
    Returns:
        Comment details
    """
    try:
        gh = GitHubTool(repo)
        result = gh.comment_on_pr(pr_number, message)
        logger.info(f"Added comment to PR #{pr_number} in repository {repo}")
        return result
    except Exception as e:
        logger.error(f"Error commenting on PR in {repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
