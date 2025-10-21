from fastapi import FastAPI
from backend.app.routers import system
from backend.app.db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="CodeOps Agent API", version="0.1.0")
    app.include_router(system.router)
    
    @app.on_event("startup")
    async def startup_event():
        await init_db()
    
    return app


app = create_app()
