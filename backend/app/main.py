from fastapi import FastAPI
from backend.app.routers import system


def create_app() -> FastAPI:
    app = FastAPI(title="CodeOps Agent API", version="0.1.0")
    app.include_router(system.router)
    return app


app = create_app()
