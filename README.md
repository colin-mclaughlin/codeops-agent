 # CodeOps Agent

MCP-powered DevOps agent that diagnoses CI failures and proposes fixes.

## Running the Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Note: Copy `.env.example` to `.env` if you need to customize configuration.
