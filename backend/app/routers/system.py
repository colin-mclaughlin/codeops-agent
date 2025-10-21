from fastapi import APIRouter

router = APIRouter(prefix="", tags=["system"])


@router.get("/healthz")
def health() -> dict:
    return {"ok": True, "service": "codeops-agent", "version": "0.1.0"}


@router.get("/")
def root() -> dict:
    return {"service": "codeops-agent", "status": "ready"}
