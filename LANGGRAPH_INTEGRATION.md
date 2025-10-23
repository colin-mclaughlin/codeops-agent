# LangGraph Integration

The CodeOps Agent now includes a **LangGraph/ReAct-style reasoning loop** for advanced decision-making and reflection. This upgrade provides structured multi-step reasoning, dynamic tool planning, and intelligent retry mechanisms while preserving all existing functionality.

## Features

### Advanced Reasoning Pipeline
- **Multi-step reasoning**: Context analysis → Planning → Reflection → Execution
- **Dynamic tool planning**: AI-driven decision making for tool selection and execution
- **Intelligent reflection**: Self-evaluation and plan improvement
- **Context-aware analysis**: Leverages FAISS retrieval for relevant context
- **Slack integration**: Real-time updates throughout the reasoning process

### Reasoning Steps
1. **Context Retrieval**: Fetches relevant context from FAISS vector store
2. **Context Analysis**: AI analyzes context to identify issues and patterns
3. **Action Planning**: Generates concrete, actionable plans
4. **Plan Reflection**: Reviews and improves the generated plan
5. **Plan Execution**: Simulates execution (extensible to real tool operations)
6. **Summary & Notification**: Sends results to Slack and logs

## Architecture

### LangGraphOrchestrator Class
The core reasoning engine that implements the LangGraph-style pipeline:

```python
class LangGraphOrchestrator:
    def __init__(self, repo_name: str)
    async def think(self, prompt: str, context: str = "") -> str
    async def analyze_context(self, context_snippets: List[str]) -> Dict[str, Any]
    async def plan_actions(self, analysis: str, context: str) -> Dict[str, Any]
    async def reflect_and_validate(self, plan: str, context: str) -> Dict[str, Any]
    async def execute_plan(self, plan: str) -> Dict[str, Any]
    async def run_pipeline(self, commit_sha: str = "latest") -> Dict[str, Any]
```

### Integration Points
- **AgentOrchestrator**: Extended with `run_langgraph()` method
- **GitHub Integration**: Uses GitHubTool for repository context
- **Slack Integration**: Sends real-time updates and summaries
- **FAISS Retrieval**: Leverages existing context retrieval system

## Setup

### 1. Environment Configuration
Ensure your `.env` file includes:
```bash
OPENAI_API_KEY=your_openai_api_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
GITHUB_TOKEN=your_github_token_here
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

### LangGraph Endpoint

#### GET `/agent/langgraph`
Run the full LangGraph reasoning pipeline.

**Parameters:**
- `commit_sha` (optional): Commit SHA for context retrieval (default: "latest")
- `repo` (optional): GitHub repository in format "username/repo-name" (default: "octocat/Hello-World")

**Example:**
```bash
GET /agent/langgraph?commit_sha=abc123&repo=username/repo-name
```

**Response:**
```json
{
  "verdict": "success",
  "latency": 41.87,
  "commit_sha": "abc123",
  "context_analysis": {
    "snippet_count": 5,
    "analysis": "### Structured Analysis of CI/CD Context Snippets...",
    "context_preview": "Snippet 1: Build failed due to..."
  },
  "action_plan": {
    "plan": "### Action Plan to Fix CI/CD Build Failures...",
    "analysis": "Previous analysis results...",
    "timestamp": "2025-10-23T20:20:11.123456"
  },
  "reflection": {
    "reflection": "### Reflection on the Action Plan...",
    "plan": "Original plan...",
    "timestamp": "2025-10-23T20:20:45.789012"
  },
  "execution": {
    "status": "simulated_success",
    "actions_taken": [
      "Analyzed build logs",
      "Identified configuration issue",
      "Prepared fix implementation",
      "Validated solution approach"
    ],
    "execution_time": 0.5,
    "timestamp": "2025-10-23T20:20:46.123456"
  },
  "timestamp": "2025-10-23T20:20:46.123456"
}
```

## Usage Examples

### Basic Usage
```python
from backend.app.agent.reasoning_langgraph import LangGraphOrchestrator

# Initialize with repository
graph = LangGraphOrchestrator("username/repo-name")

# Run full reasoning pipeline
result = await graph.run_pipeline("commit_sha_here")
print(f"Verdict: {result['verdict']}")
print(f"Latency: {result['latency']:.2f}s")
```

### Through AgentOrchestrator
```python
from backend.app.agent.reasoning import AgentOrchestrator

agent = AgentOrchestrator(db_session)
result = await agent.run_langgraph("commit_sha", "username/repo-name")
```

### Custom Reasoning Steps
```python
# Individual reasoning steps
analysis = await graph.analyze_context(context_snippets)
plan = await graph.plan_actions(analysis["analysis"], context)
reflection = await graph.reflect_and_validate(plan["plan"], context)
```

## Reasoning Process

### 1. Context Analysis
The AI analyzes retrieved context snippets to identify:
- Primary failure points or issues
- Error patterns or common causes
- Dependencies or configuration problems
- Potential root causes

### 2. Action Planning
Based on the analysis, the AI creates:
- Concrete steps to take
- Required tools/operations
- Complexity and risk assessment
- Validation steps

### 3. Plan Reflection
The AI reviews the plan to identify:
- Potential risks or edge cases
- Improvements or alternatives
- Missing steps
- Success likelihood assessment

### 4. Execution Simulation
Currently simulates execution but is designed to be extended with:
- Real GitHub operations (commits, PRs, etc.)
- Test execution and validation
- Error handling and retries
- Tool-specific operations

## Slack Integration

The LangGraph pipeline sends real-time updates to Slack:

### Plan Notification
```
:brain: 🤖 **CodeOps Agent Plan**

### Action Plan to Fix CI/CD Build Failures

1. **Immediate Code Fix**:
   - **Action**: Review the failing test cases...
```

### Reflection Notification
```
:mag: 🔍 **Plan Reflection**

### Reflection on the Action Plan to Fix CI/CD Build Failures

#### 1. Identify Potential Risks or Edge Cases
- **Risk**: The proposed fix might not address...
```

### Final Summary
```
:gear: :green_heart: *CodeOps Agent Run Summary*
• Repository: octocat/Hello-World
• Verdict: success
• Run ID: 1234
_Time: 2025-10-23T20:20:46.123456Z_
```

## Performance Characteristics

### Typical Latency
- **Full pipeline**: 40-45 seconds
- **Context retrieval**: ~1-2 seconds
- **AI reasoning steps**: ~35-40 seconds total
- **Slack notifications**: ~1-2 seconds

### Resource Usage
- **OpenAI API calls**: 3-4 calls per pipeline run
- **Token usage**: ~2000-3000 tokens per run
- **Memory**: Minimal additional overhead
- **Network**: FAISS retrieval + OpenAI + Slack calls

## Error Handling

### OpenAI API Failures
- **Retry logic**: Up to 3 attempts with exponential backoff
- **Fallback**: Graceful degradation with error messages
- **Logging**: Detailed error logging for debugging

### Context Retrieval Failures
- **Graceful handling**: Continues with empty context if retrieval fails
- **Logging**: Warns about missing context but doesn't fail pipeline

### Slack Notification Failures
- **Non-blocking**: Pipeline continues even if Slack fails
- **Error logging**: Detailed logging of Slack failures

## Testing

Run the comprehensive LangGraph integration test:
```bash
python test_langgraph_integration.py
```

This tests:
- Default parameter execution
- Specific commit SHA handling
- Different repository contexts
- Error handling and edge cases

## Extensibility

### Adding New Tools
The LangGraph pipeline is designed to be extended with additional tools:

```python
async def execute_plan(self, plan: str) -> Dict[str, Any]:
    # Parse plan for specific actions
    if "git" in plan.lower():
        await self.github.create_branch("main", "fix-branch")
        await self.github.commit_and_push("fix-branch", "file.py", content, "Fix issue")
    
    if "test" in plan.lower():
        # Execute test runner tool
        pass
```

### Custom Reasoning Steps
Add new reasoning steps by extending the pipeline:

```python
async def run_pipeline(self, commit_sha: str):
    # Existing steps...
    
    # New step: Custom validation
    validation = await self.validate_plan(plan_result["plan"])
    
    # Continue with execution...
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not configured"**
   - Ensure the API key is set in your `.env` file
   - Verify the key is valid and has sufficient credits

2. **"LangGraph pipeline failed"**
   - Check OpenAI API connectivity
   - Verify FAISS retrieval is working
   - Check Slack webhook configuration

3. **High latency (>60 seconds)**
   - Check OpenAI API response times
   - Verify network connectivity
   - Consider reducing context snippet count

### Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger("backend.app.agent.reasoning_langgraph").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Real tool execution**: Replace simulation with actual GitHub operations
- **Multi-agent coordination**: Multiple specialized reasoning agents
- **Learning from feedback**: Improve reasoning based on success/failure
- **Custom reasoning templates**: Repository-specific reasoning patterns
- **Parallel execution**: Concurrent reasoning for multiple issues

### Integration Opportunities
- **CI/CD webhooks**: Trigger reasoning on build failures
- **GitHub Actions**: Integrate with workflow runs
- **Monitoring systems**: Connect with observability platforms
- **Issue tracking**: Link with Jira, Linear, or GitHub Issues
