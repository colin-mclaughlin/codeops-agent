# GitHub Integration

The CodeOps Agent now includes direct GitHub integration using the PyGithub library, allowing the agent to interact with GitHub repositories for enhanced context and automation.

## Features

### Repository Context
- **Read commits**: Fetch recent commits with author, message, and date information
- **Workflow runs**: Retrieve GitHub Actions workflow run status and results
- **Repository info**: Get basic repository metadata (stars, forks, description, etc.)

### Repository Operations
- **Branch management**: Create new branches from existing ones
- **File operations**: Update or create files with commit messages
- **Pull requests**: Create new pull requests with custom titles and descriptions
- **Comments**: Post comments on existing pull requests

## Setup

### 1. Environment Configuration
Set your GitHub token in the `.env` file:
```bash
GITHUB_TOKEN=your_github_token_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
cd backend
uvicorn app.main:app --reload
```

## API Endpoints

### GitHub Router (`/github`)

#### GET `/github/commits`
Get recent commits from a repository.
- **Parameters**: `repo` (required), `limit` (optional, default: 5)
- **Example**: `GET /github/commits?repo=octocat/Hello-World&limit=3`

#### GET `/github/workflows`
Get recent workflow runs from a repository.
- **Parameters**: `repo` (required), `limit` (optional, default: 5)
- **Example**: `GET /github/workflows?repo=octocat/Hello-World&limit=3`

#### GET `/github/repo-info`
Get basic repository information.
- **Parameters**: `repo` (required)
- **Example**: `GET /github/repo-info?repo=octocat/Hello-World`

#### POST `/github/branch`
Create a new branch from a base branch.
- **Parameters**: `repo`, `base`, `new_branch`
- **Example**: `POST /github/branch` with JSON body

#### POST `/github/commit`
Update a file and commit changes.
- **Parameters**: `repo`, `branch`, `file_path`, `content`, `message`
- **Example**: `POST /github/commit` with JSON body

#### POST `/github/pull-request`
Create a new pull request.
- **Parameters**: `repo`, `title`, `body`, `head`, `base` (optional, default: "main")
- **Example**: `POST /github/pull-request` with JSON body

#### POST `/github/comment`
Add a comment to a pull request.
- **Parameters**: `repo`, `pr_number`, `message`
- **Example**: `POST /github/comment` with JSON body

### Agent Router (`/agent`)

#### GET `/agent/github-context`
Test GitHub integration through the agent orchestrator.
- **Parameters**: `repo` (optional, default: "octocat/Hello-World")
- **Example**: `GET /agent/github-context?repo=your-username/your-repo`

## Usage Examples

### Fetch Repository Context
```python
from backend.app.agent.github_tool import GitHubTool

# Initialize with repository
gh = GitHubTool("username/repo-name")

# Get recent commits
commits = gh.list_recent_commits(limit=5)

# Get workflow runs
workflows = gh.get_workflow_runs(limit=3)

# Get repository info
info = gh.get_repository_info()
```

### Create and Manage Pull Requests
```python
# Create a new branch
gh.create_branch("main", "feature/new-feature")

# Update a file
gh.commit_and_push("feature/new-feature", "README.md", "Updated content", "Update README")

# Create a pull request
pr = gh.open_pull_request(
    title="Add new feature",
    body="This PR adds a new feature to the project",
    head="feature/new-feature",
    base="main"
)

# Comment on the PR
gh.comment_on_pr(pr["number"], "Great work! This looks good to me.")
```

## Testing

Run the GitHub integration test script:
```bash
python test_github_integration.py
```

This will test all GitHub endpoints with a public repository and verify the integration is working correctly.

## Integration with Agent Orchestrator

The GitHub integration is built into the `AgentOrchestrator` class through the `github_actions()` method, which can be called during the pipeline execution to fetch repository context before planning fixes.

```python
# In your agent pipeline
agent = AgentOrchestrator(db_session)
github_context = await agent.github_actions("username/repo-name")
```

## Error Handling

All GitHub operations include comprehensive error handling and logging. Errors are logged with detailed information and appropriate HTTP status codes are returned for API endpoints.

## Security

- GitHub tokens are loaded from environment variables
- All operations respect GitHub API rate limits
- Repository access is controlled by the provided GitHub token permissions
