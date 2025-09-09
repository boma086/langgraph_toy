"""FastAPI application for LangGraph toy API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, Optional
import logging
from api.endpoints import router
from api.models import ExecuteRequest, ExecuteResponse, ChatRequest, ChatResponse, GraphStateRequest, GraphStateResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="LangGraph Toy API",
        description="A custom LangGraph implementation with web interface",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API endpoints
    app.include_router(router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "message": "LangGraph Toy API is running"}
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "LangGraph Toy API", "docs": "/docs"}
    
    @app.get("/web")
    async def web_interface():
        """Web interface redirect."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/")
    
    # Mount static files for web interface (must be last)
    app.mount("/web/", StaticFiles(directory="web/static", html=True), name="static")
    
    return app


