 # CodeOps Agent

MCP-powered DevOps agent that diagnoses CI failures and proposes fixes.

## Running the Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Note: Copy `.env.example` to `.env` if you need to customize configuration.

## API Endpoints

### Trigger Agent Pipeline
```bash
POST http://127.0.0.1:8000/agent/run/1
```

This endpoint triggers the full agent pipeline for a specific RunLog ID, including context retrieval, planning, tool execution, and result storage.
