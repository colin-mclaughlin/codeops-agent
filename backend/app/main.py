from fastapi import FastAPI
from backend.app.routers import system, webhook, metrics, agent
from backend.app.db import init_db
from backend.app.utils.logging import setup_logging
# Import models to ensure they're registered with Base.metadata
from backend.app.models import run_log
from backend.app.agent import reasoning


def create_app() -> FastAPI:
    # Setup logging first
    setup_logging()
    
    app = FastAPI(title="CodeOps Agent API", version="0.1.0")
    app.include_router(system.router)
    app.include_router(webhook.router)
    app.include_router(metrics.router)
    app.include_router(agent.router)
    
    @app.on_event("startup")
    async def startup_event():
        await init_db()
    
    return app


app = create_app()
