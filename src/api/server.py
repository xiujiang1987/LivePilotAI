from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Basic Pydantic models for the health check
class HealthStatus(BaseModel):
    status: str
    version: str
    is_running: bool = False

from src.api.routes import core, control

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="LivePilotAI API",
        description="API for LivePilotAI OBS and AI control",
        version="1.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def root():
        """Redirect root to the static dashboard"""
        return RedirectResponse(url="/static/index.html")

    app.include_router(core.router)
    app.include_router(control.router)

    @app.get("/api/v1/health", response_model=HealthStatus, tags=["System"])
    async def health_check():
        """Basic health check endpoint."""
        # Optional: check if app exists in state and is running
        is_running = getattr(app.state, "main_app", None) is not None
        return HealthStatus(status="ok", version="1.1.0", is_running=is_running)

    return app

def get_app_instance() -> FastAPI:
    """Return the global app instance for uvicorn"""
    return app

# Expose app for Uvicorn
app = create_app()
