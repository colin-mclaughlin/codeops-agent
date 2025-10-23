from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import system, webhook, metrics, agent, runs, context, github
from backend.app.db import init_db
from backend.app.utils.logging import setup_logging
# Import models to ensure they're registered with Base.metadata
from backend.app.models import run_log
from backend.app.agent import reasoning


def create_app() -> FastAPI:
    # Setup logging first
    setup_logging()
    
    app = FastAPI(title="CodeOps Agent API", version="0.1.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(system.router)
    app.include_router(webhook.router)
    app.include_router(metrics.router)
    app.include_router(agent.router)
    app.include_router(runs.router)
    app.include_router(context.router)
    app.include_router(github.router)
    
    @app.on_event("startup")
    async def startup_event():
        await init_db()
        # Initialize retrieval store with default contexts
        from backend.app.retrieval import initialize_retrieval_store
        await initialize_retrieval_store()
    
    return app


app = create_app()
