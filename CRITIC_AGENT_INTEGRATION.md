# Critic Agent Integration

The CodeOps Agent now includes a **Critic Agent** that creates a two-agent loop for improved reliability and decision transparency. The critic reviews the main agent's output before finalization, providing quality assessment, risk identification, and confidence scoring.

## Features

### Two-Agent Architecture
- **Primary Agent**: LangGraph reasoning pipeline (plan → execute → reflect)
- **Critic Agent**: Secondary reviewer that critiques primary agent output
- **Quality Assessment**: Confidence scoring (0-100) for plan and reflection quality
- **Risk Identification**: Highlights potential issues and missing considerations
- **Improvement Suggestions**: Provides specific recommendations for better outcomes

### Critic Capabilities
- **Plan Review**: Analyzes action plans for completeness and feasibility
- **Reflection Review**: Evaluates self-awareness and depth of reflection
- **Context Integration**: Considers additional context for better assessment
- **Confidence Scoring**: Provides quantitative quality assessment
- **Slack Integration**: Sends critique summaries to configured channels
- **Metrics Tracking**: Records critic runs and average confidence scores

## Architecture

### CriticAgent Class
The core critic implementation that provides quality assessment:

```python
class CriticAgent:
    def __init__(self)
    async def critique(self, plan: str, reflection: str, context: str = "") -> Dict[str, Any]
    async def quick_review(self, plan: str) -> Dict[str, Any]
    def get_critique_summary(self, critique_result: Dict[str, Any]) -> str
    def _extract_confidence_score(self, critique_text: str) -> int
```

### Integration Points
- **LangGraphOrchestrator**: Integrated as Step 8 in the reasoning pipeline
- **Metrics System**: Tracks critic runs and average confidence scores
- **Slack Notifications**: Sends formatted critique summaries
- **API Endpoints**: Standalone critic review capabilities

## Setup

### 1. Environment Configuration
Ensure your `.env` file includes:
```bash
OPENAI_API_KEY=your_openai_api_key_here
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

### Critic Router (`/critic`)

#### POST `/critic/review`
Review primary agent's plan and reflection.

**Request Body:**
```json
{
  "plan": "Fix the build error by updating configuration",
  "reflection": "This plan addresses the root cause",
  "context": "Build failed due to missing environment variable"
}
```

**Response:**
```json
{
  "critique": "### Key Strengths\n- **Direct Approach**: The agent identifies...",
  "confidence": 75,
  "timestamp": "2025-10-23T20:42:46.123456",
  "plan_length": 45,
  "reflection_length": 32
}
```

#### POST `/critic/quick-review`
Perform a quick review of just the plan.

**Request Body:**
```json
{
  "plan": "Implement automated testing for CI/CD pipeline"
}
```

**Response:**
```json
{
  "critique": "### Feasibility Assessment\nThis plan is well-structured...",
  "confidence": 80,
  "timestamp": "2025-10-23T20:42:46.123456",
  "type": "quick_review"
}
```

#### POST `/critic/summary`
Get a formatted summary of a critique for display.

**Request Body:**
```json
{
  "plan": "Deploy fix to production after testing",
  "reflection": "This approach ensures safety",
  "context": "Production deployment needed"
}
```

**Response:**
```json
{
  "summary": "🧠 **Critic Review** (Confidence: 75/100)\n\n• Key Strengths...",
  "confidence": 75,
  "timestamp": "2025-10-23T20:42:46.123456"
}
```

## Integration with LangGraph Pipeline

The critic is integrated as Step 8 in the LangGraph reasoning pipeline:

1. **Context Retrieval**: Fetches relevant context from FAISS
2. **Context Analysis**: AI analyzes context for issues and patterns
3. **Action Planning**: Generates concrete, actionable plans
4. **Plan Reflection**: Reviews and improves the generated plan
5. **Plan Execution**: Simulates execution (extensible to real tools)
6. **Critic Review**: **NEW** - Critic agent reviews plan and reflection
7. **Critic Notification**: Sends critique summary to Slack
8. **Final Summary**: Sends final results to Slack and logs

### LangGraph Response with Critic
The `/agent/langgraph` endpoint now includes critic data:

```json
{
  "verdict": "success",
  "latency": 46.67,
  "commit_sha": "critic_test",
  "context_analysis": { ... },
  "action_plan": { ... },
  "reflection": { ... },
  "execution": { ... },
  "critique": {
    "critique": "### Key Strengths\n- **Comprehensive Analysis**...",
    "confidence": 75,
    "timestamp": "2025-10-23T20:42:46.123456",
    "plan_length": 1234,
    "reflection_length": 567
  },
  "timestamp": "2025-10-23T20:42:46.123456"
}
```

## Metrics Integration

The metrics system now tracks critic performance:

### Updated Metrics Endpoint
```bash
GET /metrics
```

**Response:**
```json
{
  "runs": 0,
  "success_rate": 0,
  "avg_latency_ms": 1300,
  "critic_runs": 2,
  "avg_confidence": 67.5
}
```

### Metrics Functions
- `record_critic(confidence: int)`: Records a critic run with confidence score
- Automatic tracking of critic runs and average confidence
- Integration with existing metrics system

## Usage Examples

### Standalone Critic Review
```python
from backend.app.agent.critic_agent import CriticAgent

critic = CriticAgent()
result = await critic.critique(
    plan="Fix build error by updating config",
    reflection="This addresses the root cause",
    context="Build failed due to missing env var"
)
print(f"Confidence: {result['confidence']}/100")
```

### Through API
```python
import requests

response = requests.post("http://localhost:8000/critic/review", json={
    "plan": "Implement automated testing",
    "reflection": "This will prevent future failures",
    "context": "CI/CD pipeline needs better validation"
})
critique = response.json()
print(f"Critic confidence: {critique['confidence']}")
```

### LangGraph with Critic
```python
# The critic is automatically integrated
response = requests.get("http://localhost:8000/agent/langgraph?commit_sha=abc123")
result = response.json()
print(f"Critic confidence: {result['critique']['confidence']}")
```

## Critic Review Process

### 1. Input Analysis
The critic receives:
- **Plan**: Primary agent's action plan
- **Reflection**: Primary agent's self-reflection
- **Context**: Additional context from FAISS retrieval

### 2. Quality Assessment
The critic evaluates:
- **Key Strengths**: What the agent did well
- **Weaknesses & Risks**: Potential issues or missing elements
- **Confidence Assessment**: Score 0-100 with justification
- **Improvement Suggestions**: Specific recommendations

### 3. Output Generation
The critic provides:
- **Structured critique**: Organized feedback with clear sections
- **Confidence score**: Quantitative quality assessment (0-100)
- **Metadata**: Timestamps, input lengths, processing details
- **Slack summary**: Formatted summary for notifications

## Confidence Scoring

### Score Interpretation
- **90-100**: Excellent plan with minimal risks
- **70-89**: Good plan with minor concerns
- **50-69**: Adequate plan with some issues
- **30-49**: Poor plan with significant concerns
- **0-29**: Very poor plan with major risks

### Score Extraction
The critic uses pattern matching to extract confidence scores:
- Looks for "confidence: X", "score: X", "X%", "X/100"
- Falls back to any number 0-100 in the response
- Defaults to 70 if no score is found

## Slack Integration

### Critic Notifications
The critic sends formatted summaries to Slack:

```
:mag_right: 🧠 **Critic Review** (Confidence: 75/100)

• ### Key Strengths
• ### Weaknesses & Risks
• - **No Contingency Plans**: There is no mention of rollback procedures...
```

### Notification Flow
1. **Plan Notification**: Primary agent sends plan to Slack
2. **Reflection Notification**: Primary agent sends reflection to Slack
3. **Critic Notification**: **NEW** - Critic sends review summary to Slack
4. **Final Summary**: Primary agent sends final results to Slack

## Performance Characteristics

### Typical Latency
- **Critic review**: ~15-20 seconds
- **Quick review**: ~8-12 seconds
- **Full LangGraph with critic**: ~45-50 seconds
- **Total overhead**: ~15-20 seconds per pipeline run

### Resource Usage
- **OpenAI API calls**: 1 additional call per critic review
- **Token usage**: ~800-1200 tokens per critic review
- **Memory**: Minimal additional overhead
- **Network**: Additional OpenAI API call

## Error Handling

### OpenAI API Failures
- **Retry logic**: Up to 3 attempts with exponential backoff
- **Fallback**: Graceful degradation with error messages
- **Logging**: Detailed error logging for debugging

### Confidence Score Extraction
- **Pattern matching**: Multiple patterns for score extraction
- **Fallback logic**: Defaults to 70 if no score found
- **Error handling**: Graceful handling of extraction failures

### Integration Failures
- **Non-blocking**: LangGraph pipeline continues even if critic fails
- **Error logging**: Detailed logging of critic failures
- **Metrics tracking**: Failed critic runs are still tracked

## Testing

Run the comprehensive critic integration test:
```bash
python test_critic_integration.py
```

This tests:
- Standalone critic review functionality
- Quick review capabilities
- LangGraph integration with critic
- Metrics tracking and reporting
- Summary generation
- Error handling and edge cases

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not configured"**
   - Ensure the API key is set in your `.env` file
   - Verify the key is valid and has sufficient credits

2. **"Critic review failed"**
   - Check OpenAI API connectivity
   - Verify the API key has sufficient credits
   - Check for rate limiting issues

3. **Low confidence scores**
   - Review the input plan and reflection quality
   - Check if context is being provided effectively
   - Consider adjusting the critic's system prompt

4. **Missing critic data in metrics**
   - Ensure critic is being called in the LangGraph pipeline
   - Check that `record_critic()` is being called
   - Verify metrics endpoint is returning updated data

### Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger("backend.app.agent.critic_agent").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Multi-critic consensus**: Multiple critics for better assessment
- **Learning from feedback**: Improve based on success/failure patterns
- **Custom critique templates**: Repository-specific critique patterns
- **Confidence calibration**: Better confidence score accuracy
- **Critic specialization**: Different critics for different types of plans

### Integration Opportunities
- **Quality gates**: Block low-confidence plans from execution
- **Feedback loops**: Use critic feedback to improve primary agent
- **A/B testing**: Compare plans with and without critic review
- **Analytics**: Detailed analysis of critic performance over time

## Benefits

### Improved Reliability
- **Quality assurance**: Second opinion on all plans
- **Risk identification**: Early detection of potential issues
- **Confidence scoring**: Quantitative assessment of plan quality

### Better Decision Transparency
- **Clear feedback**: Structured critique with specific recommendations
- **Audit trail**: Complete record of critic assessments
- **Metrics tracking**: Long-term performance monitoring

### Enhanced User Experience
- **Real-time updates**: Slack notifications throughout the process
- **Detailed insights**: Rich feedback on plan quality
- **Confidence indicators**: Clear quality signals for decision making
