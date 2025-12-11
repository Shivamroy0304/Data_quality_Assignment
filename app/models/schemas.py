"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class NodeInput(BaseModel):
    """Input for defining a node in the API."""
    name: str
    description: Optional[str] = ""


class EdgeInput(BaseModel):
    """Input for defining an edge in the API."""
    from_node: str
    to_node: str
    description: Optional[str] = ""


class GraphCreateRequest(BaseModel):
    """Request to create a new graph."""
    name: str
    entry_point: str
    nodes: List[NodeInput]
    edges: List[EdgeInput]


class GraphCreateResponse(BaseModel):
    """Response after creating a graph."""
    graph_id: str
    name: str
    created_at: datetime
    nodes: List[str]
    entry_point: str


class GraphRunRequest(BaseModel):
    """Request to run a graph."""
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class ExecutionLogEntry(BaseModel):
    """Log entry for workflow execution."""
    step_id: str
    node_name: str
    timestamp: datetime
    status: str
    error: Optional[str] = None
    duration_ms: float


class GraphRunResponse(BaseModel):
    """Response after running a graph."""
    run_id: str
    graph_id: str
    status: str
    final_state: Dict[str, Any]
    visited_nodes: List[str]
    logs: List[ExecutionLogEntry]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class GraphStateResponse(BaseModel):
    """Response with current graph state."""
    run_id: str
    graph_id: str
    status: str
    current_state: Dict[str, Any]
    visited_nodes: List[str]
    logs: List[ExecutionLogEntry]


class ToolInfo(BaseModel):
    """Information about a registered tool."""
    name: str
    description: str


class ToolsListResponse(BaseModel):
    """Response listing available tools."""
    tools: List[ToolInfo]
