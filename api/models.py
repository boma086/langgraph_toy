"""Pydantic models for API requests and responses."""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class ExecuteRequest(BaseModel):
    """Request model for graph execution."""
    graph_type: str
    input_data: Dict[str, Any]


class ExecuteResponse(BaseModel):
    """Response model for graph execution."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    execution_time: float
    error: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str
    agent_type: str = "simple"


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response: str
    agent_type: str
    timestamp: float


class GraphStateRequest(BaseModel):
    """Request model for state operations."""
    state_data: Dict[str, Any]
    operation: str  # "get", "set", "update"


class GraphStateResponse(BaseModel):
    """Response model for state operations."""
    success: bool
    state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None