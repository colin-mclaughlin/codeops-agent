import os
import uuid
from github import Github
from backend.app.utils.logging import get_logger
from backend.app.config import settings
from backend.app.agent.safety import (
    validate_branch_name, 
    log_operation, 
    check_github_token,
    is_dry_run_mode
)


class GitHubTool:
    """
    MCP tool for interacting with GitHub repositories.
    """

    def __init__(self, repo_name: str):
        """
        Initialize GitHub tool with repository name.
        
        Args:
            repo_name: GitHub repository in format "username/repo-name"
        """
        self.logger = get_logger(__name__)
        self.repo_name = repo_name
        
        # Get GitHub token from settings with safety check
        if not check_github_token():
            raise ValueError("GITHUB_TOKEN environment variable is required and valid")
        
        github_token = settings.GITHUB_TOKEN
        self.client = Github(github_token)
        self.repo = self.client.get_repo(repo_name)
        self.logger.info(f"GitHubTool initialized for repository: {repo_name}")
        
        # Log initialization
        log_operation("GitHubTool_Init", {
            "repo_name": repo_name,
            "dry_run_mode": is_dry_run_mode()
        })

    def list_recent_commits(self, limit: int = 5):
        """
        Get recent commits from the repository.
        
        Args:
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries with sha, message, and author
        """
        try:
            commits = self.repo.get_commits()[:limit]
            result = []
            for c in commits:
                result.append({
                    "sha": c.sha,
                    "message": c.commit.message,
                    "author": c.commit.author.name,
                    "date": c.commit.author.date.isoformat() if c.commit.author.date else None
                })
            self.logger.info(f"Retrieved {len(result)} recent commits")
            return result
        except Exception as e:
            self.logger.error(f"Error retrieving commits: {e}")
            raise

    def get_workflow_runs(self, limit: int = 5):
        """
        Get recent workflow runs from the repository.
        
        Args:
            limit: Maximum number of workflow runs to return per workflow
            
        Returns:
            List of workflow run dictionaries
        """
        try:
            workflows = self.repo.get_workflows()
            runs = []
            for wf in workflows:
                for run in wf.get_runs()[:limit]:
                    runs.append({
                        "workflow": wf.name,
                        "status": run.status,
                        "conclusion": run.conclusion,
                        "url": run.html_url,
                        "created_at": run.created_at.isoformat() if run.created_at else None,
                        "run_id": run.id
                    })
            self.logger.info(f"Retrieved {len(runs)} workflow runs")
            return runs
        except Exception as e:
            self.logger.error(f"Error retrieving workflow runs: {e}")
            raise

    def create_branch(self, base: str, new_branch: str):
        """
        Create a new branch from a base branch.
        
        Args:
            base: Base branch name (e.g., "main")
            new_branch: New branch name
            
        Returns:
            Dictionary with branch creation details
        """
        try:
            # Safety checks
            if not validate_branch_name(new_branch):
                # Auto-fix branch name if it doesn't have agent prefix
                if not new_branch.startswith('agent-fix/'):
                    new_branch = f"agent-fix/{new_branch}"
                    if not validate_branch_name(new_branch):
                        raise ValueError(f"Invalid branch name: {new_branch}")
            
            # Check dry run mode
            if is_dry_run_mode():
                self.logger.info(f"DRY RUN: Would create branch '{new_branch}' from '{base}'")
                return {"branch": new_branch, "base": base, "sha": "dry_run_sha", "dry_run": True}
            
            # Log the operation
            log_operation("Create_Branch", {
                "branch": new_branch,
                "base": base,
                "repo": self.repo_name
            })
            
            ref = self.repo.get_git_ref(f"heads/{base}")
            self.repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=ref.object.sha)
            self.logger.info(f"Created branch '{new_branch}' from '{base}'")
            return {"branch": new_branch, "base": base, "sha": ref.object.sha}
        except Exception as e:
            self.logger.error(f"Error creating branch: {e}")
            raise

    def commit_and_push(self, branch: str, file_changes: list[dict], message: str):
        """
        Update multiple files and commit the changes.
        
        Args:
            branch: Branch name to commit to
            file_changes: List of dictionaries with 'path' and 'content' keys
            message: Commit message
            
        Returns:
            Dictionary with commit details
        """
        try:
            # Safety checks
            if not validate_branch_name(branch):
                raise ValueError(f"Invalid branch name: {branch}")
            
            # Check dry run mode
            if is_dry_run_mode():
                self.logger.info(f"DRY RUN: Would commit {len(file_changes)} files to branch '{branch}'")
                return {
                    "branch": branch,
                    "files": [change["path"] for change in file_changes],
                    "message": message,
                    "commit_sha": "dry_run_sha",
                    "dry_run": True
                }
            
            # Log the operation
            log_operation("Commit_And_Push", {
                "branch": branch,
                "file_count": len(file_changes),
                "files": [change["path"] for change in file_changes],
                "message": message,
                "repo": self.repo_name
            })
            
            commit_files = []
            
            for change in file_changes:
                file_path = change["path"]
                content = change["content"]
                
                # Try to get existing file content
                try:
                    contents = self.repo.get_contents(file_path, ref=branch)
                    # Update existing file
                    commit_files.append({
                        "path": contents.path,
                        "content": content,
                        "sha": contents.sha
                    })
                    self.logger.info(f"Prepared update for file '{file_path}' on branch '{branch}'")
                except Exception:
                    # File doesn't exist, create new file
                    commit_files.append({
                        "path": file_path,
                        "content": content
                    })
                    self.logger.info(f"Prepared creation of file '{file_path}' on branch '{branch}'")
            
            # Create tree and commit
            base_tree = self.repo.get_git_tree(branch)
            tree_elements = []
            
            for file_info in commit_files:
                blob = self.repo.create_git_blob(file_info["content"], "utf-8")
                tree_elements.append({
                    "path": file_info["path"],
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob.sha
                })
            
            tree = self.repo.create_git_tree(tree_elements, base_tree)
            parent = self.repo.get_git_commit(branch)
            commit = self.repo.create_git_commit(message, tree, [parent])
            
            # Update branch reference
            ref = self.repo.get_git_ref(f"heads/{branch}")
            ref.edit(sha=commit.sha)
            
            self.logger.info(f"Committed {len(file_changes)} files to branch '{branch}'")
            
            return {
                "branch": branch, 
                "files": [change["path"] for change in file_changes],
                "message": message,
                "commit_sha": commit.sha
            }
        except Exception as e:
            self.logger.error(f"Error committing files: {e}")
            raise

    def open_pull_request(self, title: str, body: str, head: str, base: str = "main"):
        """
        Create a new pull request.
        
        Args:
            title: PR title
            body: PR description
            head: Source branch name
            base: Target branch name (default: "main")
            
        Returns:
            Dictionary with PR details
        """
        try:
            pr = self.repo.create_pull(title=title, body=body, head=head, base=base)
            self.logger.info(f"Created pull request #{pr.number}: {title}")
            return {
                "number": pr.number, 
                "url": pr.html_url,
                "title": title,
                "head": head,
                "base": base
            }
        except Exception as e:
            self.logger.error(f"Error creating pull request: {e}")
            raise

    def comment_on_pr(self, pr_number: int, message: str):
        """
        Add a comment to a pull request.
        
        Args:
            pr_number: Pull request number
            message: Comment message
            
        Returns:
            Dictionary with comment details
        """
        try:
            pr = self.repo.get_pull(pr_number)
            comment = pr.create_issue_comment(message)
            self.logger.info(f"Added comment to PR #{pr_number}")
            return {
                "comment_id": comment.id, 
                "url": pr.html_url,
                "pr_number": pr_number
            }
        except Exception as e:
            self.logger.error(f"Error commenting on PR: {e}")
            raise

    def get_repository_info(self):
        """
        Get basic repository information.
        
        Returns:
            Dictionary with repository details
        """
        try:
            return {
                "name": self.repo.name,
                "full_name": self.repo.full_name,
                "description": self.repo.description,
                "url": self.repo.html_url,
                "default_branch": self.repo.default_branch,
                "stars": self.repo.stargazers_count,
                "forks": self.repo.forks_count
            }
        except Exception as e:
            self.logger.error(f"Error getting repository info: {e}")
            raise

    def create_branch_with_uuid(self, base: str = "main") -> str:
        """
        Create a new branch with a UUID-based name for safety.
        
        Args:
            base: Base branch name (default: "main")
            
        Returns:
            The created branch name
        """
        branch_uuid = str(uuid.uuid4())[:8]
        branch_name = f"agent-fix/{branch_uuid}"
        result = self.create_branch(base, branch_name)
        return result["branch"]

    def commit_and_push_changes(self, branch: str, file_changes: list[dict], message: str) -> str:
        """
        Convenience method for committing and pushing changes.
        
        Args:
            branch: Branch name to commit to
            file_changes: List of dictionaries with 'path' and 'content' keys
            message: Commit message
            
        Returns:
            The commit SHA
        """
        result = self.commit_and_push(branch, file_changes, message)
        return result["commit_sha"]

    def create_pull_request(self, repo_owner: str, repo_name: str, branch: str, base: str, title: str, body: str) -> dict:
        """
        Create a pull request using the GitHub API.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            branch: Source branch name
            base: Target branch name
            title: PR title
            body: PR description
            
        Returns:
            Dictionary with PR details
        """
        return self.open_pull_request(title, body, branch, base)
