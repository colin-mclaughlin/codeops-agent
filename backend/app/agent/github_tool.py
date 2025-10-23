import os
from github import Github
from backend.app.utils.logging import get_logger
from backend.app.config import settings


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
        
        # Get GitHub token from settings
        github_token = settings.GITHUB_TOKEN
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.client = Github(github_token)
        self.repo = self.client.get_repo(repo_name)
        self.logger.info(f"GitHubTool initialized for repository: {repo_name}")

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
            ref = self.repo.get_git_ref(f"heads/{base}")
            self.repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=ref.object.sha)
            self.logger.info(f"Created branch '{new_branch}' from '{base}'")
            return {"branch": new_branch, "base": base, "sha": ref.object.sha}
        except Exception as e:
            self.logger.error(f"Error creating branch: {e}")
            raise

    def commit_and_push(self, branch: str, file_path: str, content: str, message: str):
        """
        Update a file and commit the changes.
        
        Args:
            branch: Branch name to commit to
            file_path: Path to the file to update
            content: New content for the file
            message: Commit message
            
        Returns:
            Dictionary with commit details
        """
        try:
            # Try to get existing file content
            try:
                contents = self.repo.get_contents(file_path, ref=branch)
                # Update existing file
                result = self.repo.update_file(
                    contents.path, 
                    message, 
                    content, 
                    contents.sha, 
                    branch=branch
                )
                self.logger.info(f"Updated file '{file_path}' on branch '{branch}'")
            except Exception:
                # File doesn't exist, create new file
                result = self.repo.create_file(
                    file_path,
                    message,
                    content,
                    branch=branch
                )
                self.logger.info(f"Created file '{file_path}' on branch '{branch}'")
            
            return {
                "branch": branch, 
                "file": file_path, 
                "message": message,
                "commit_sha": result["commit"].sha
            }
        except Exception as e:
            self.logger.error(f"Error committing file: {e}")
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
