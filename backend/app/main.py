from fastapi import FastAPI

app = FastAPI(title="CodeOps Agent API", version="0.1.0")

@app.get("/healthz")
def health():
    return {"ok": True, "service": "codeops-agent", "version": "0.1.0"}
