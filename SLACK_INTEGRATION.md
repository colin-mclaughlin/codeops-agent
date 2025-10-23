# Slack Integration

The CodeOps Agent now includes real-time Slack notifications using Slack's Incoming Webhooks, allowing the agent to deliver concise summaries and updates directly to configured Slack channels.

## Features

### Real-time Notifications
- **Agent run summaries**: Automatic notifications when agent runs complete (success or failure)
- **Pull request notifications**: Alerts when PRs are created, updated, merged, or closed
- **Error notifications**: Immediate alerts for critical errors or failures
- **Custom messages**: Ability to send custom messages for testing or manual notifications

### Message Types
- **Run summaries**: Include verdict, repository, run ID, and optional PR URL
- **PR notifications**: Include action type, repository, PR number, title, and GitHub URL
- **Error alerts**: Include error message and optional context information
- **Test messages**: Simple text messages for testing connectivity

## Setup

### 1. Slack Webhook Configuration
Set your Slack webhook URL in the `.env` file:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
cd backend
uvicorn backend.app.main:app --reload
```

## API Endpoints

### Slack Router (`/slack`)

#### GET `/slack/test`
Send a test message to Slack.
- **Parameters**: `msg` (optional, default: "Hello from CodeOps Agent")
- **Example**: `GET /slack/test?msg=Test%20message`

#### POST `/slack/summary`
Send a run summary to Slack.
- **Body**: JSON with `verdict`, `repo`, and optional `run_log_id`, `pr_url`
- **Example**:
```json
{
  "verdict": "success",
  "repo": "octocat/Hello-World",
  "run_log_id": 123,
  "pr_url": "https://github.com/octocat/Hello-World/pull/1"
}
```

#### POST `/slack/pr-notification`
Send a PR notification to Slack.
- **Body**: JSON with `action`, `repo`, `pr_number`, `pr_url`, and optional `title`
- **Example**:
```json
{
  "action": "created",
  "repo": "octocat/Hello-World",
  "pr_number": 1,
  "pr_url": "https://github.com/octocat/Hello-World/pull/1",
  "title": "New feature implementation"
}
```

#### POST `/slack/error`
Send an error notification to Slack.
- **Body**: JSON with `error` and optional `context`
- **Example**:
```json
{
  "error": "Build failed due to syntax error",
  "context": "Python file validation"
}
```

## Usage Examples

### Basic Message
```python
from backend.app.agent.slack_tool import SlackTool

slack = SlackTool()
result = slack.post_message("Hello from CodeOps Agent!")
```

### Run Summary
```python
# Success notification
slack.post_summary("success", "username/repo-name", run_log_id=123)

# Failure notification with PR URL
slack.post_summary("failure", "username/repo-name", 
                  pr_url="https://github.com/username/repo-name/pull/1",
                  run_log_id=124)
```

### PR Notification
```python
slack.post_pr_notification(
    action="created",
    repo="username/repo-name",
    pr_number=1,
    pr_url="https://github.com/username/repo-name/pull/1",
    title="Add new feature"
)
```

### Error Notification
```python
slack.post_error_notification(
    error="Build pipeline failed",
    context="CI/CD validation step"
)
```

## Integration with Agent Orchestrator

The Slack integration is automatically triggered during agent runs through the `report_outcome()` method in the `AgentOrchestrator` class. This ensures that every agent run completion is automatically reported to Slack.

### Automatic Notifications
- **Agent run completion**: Automatically sends summary with verdict and repository info
- **Error handling**: Graceful error handling if Slack webhook fails
- **Logging**: All Slack operations are logged for debugging

### Customization
The default repository name can be configured in the `report_outcome()` method:
```python
repo_name = "your-username/your-repo"  # Change this to your repository
```

## Message Formatting

### Run Summary Format
```
:gear: :green_heart: *CodeOps Agent Run Summary*
• Repository: username/repo-name
• Verdict: success
• Run ID: 123
• Pull Request: View on GitHub
_Time: 2025-10-23T18:22:34.123456Z_
```

### PR Notification Format
```
:octocat: :new: *Pull Request Created*
• Repository: username/repo-name
• PR #1
• Title: New feature implementation
• View on GitHub
_Time: 2025-10-23T18:22:34.123456Z_
```

### Error Notification Format
```
:rotating_light: :warning: *CodeOps Agent Error*
• Error: Build pipeline failed
• Context: CI/CD validation step
_Time: 2025-10-23T18:22:34.123456Z_
```

## Testing

Run the comprehensive Slack integration test:
```bash
python test_slack_integration.py
```

This will test all Slack endpoints and send sample messages to your configured Slack channel.

## Error Handling

- **Webhook failures**: Gracefully handled with error logging
- **Network issues**: Timeout and connection error handling
- **Invalid payloads**: Validation and error response handling
- **Missing configuration**: Clear error messages for missing webhook URL

## Security

- **Webhook URL**: Stored securely in environment variables
- **Message validation**: Input validation for all message types
- **Rate limiting**: Respects Slack's webhook rate limits
- **Error logging**: Sensitive information is not logged

## Troubleshooting

### Common Issues

1. **"SLACK_WEBHOOK_URL not configured"**
   - Ensure the webhook URL is set in your `.env` file
   - Verify the URL format is correct

2. **"Slack post failed"**
   - Check your webhook URL is still valid
   - Verify the Slack app has proper permissions
   - Check network connectivity

3. **Messages not appearing in Slack**
   - Verify the webhook is configured for the correct channel
   - Check if the Slack app is installed in your workspace
   - Ensure the webhook URL hasn't expired

### Debug Mode
Enable debug logging to see detailed Slack communication:
```python
import logging
logging.getLogger("backend.app.agent.slack_tool").setLevel(logging.DEBUG)
```
