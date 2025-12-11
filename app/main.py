"""
FastAPI application for the workflow engine.

Exposes REST API endpoints for:
- Creating workflows
- Running workflows
- Checking workflow status
- Managing tools
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.graph import Graph, WorkflowExecutor
from app.core.storage import get_graph_store, get_run_store
from app.core.tools import get_tool_registry
from app.models.schemas import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    GraphStateResponse,
    ExecutionLogEntry,
    ToolInfo,
    ToolsListResponse,
)
from app.workflows.data_quality import create_data_quality_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Workflow Engine API",
    description="A lightweight workflow/graph engine with state management",
    version="1.0.0"
)

# Get storage instances
graph_store = get_graph_store()
run_store = get_run_store()
tool_registry = get_tool_registry()


# ============================================================================
# Pre-register Example Workflows
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize built-in workflows on startup."""
    logger.info("Initializing built-in workflows...")
    
    # Create and register data quality pipeline
    dq_graph = create_data_quality_pipeline()
    graph_store.save(dq_graph)
    logger.info(f"Registered data quality pipeline: {dq_graph.graph_id}")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Graph Management Endpoints
# ============================================================================

@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(request: GraphCreateRequest):
    """
    Create a new workflow graph.
    
    Args:
        request: Graph creation request with nodes and edges
    
    Returns:
        Created graph information with graph_id
    """
    try:
        # Create graph
        graph = Graph(name=request.name)
        
        # Add nodes
        for node in request.nodes:
            # Create a simple passthrough function for API-defined nodes
            # In production, this would load actual node implementations
            def node_func(state, node_name=node.name):
                # Simple pass-through: just update iteration counter
                return {"last_node": node_name}
            
            graph.add_node(node.name, node_func, node.description)
        
        # Add edges
        for edge in request.edges:
            graph.add_edge(edge.from_node, edge.to_node, description=edge.description)
        
        # Set entry point
        graph.set_entry_point(request.entry_point)
        
        # Validate
        is_valid, error_msg = graph.validate()
        if not is_valid:
            raise ValueError(f"Invalid graph: {error_msg}")
        
        # Store graph
        graph_store.save(graph)
        
        logger.info(f"Created graph: {graph.graph_id}")
        
        return GraphCreateResponse(
            graph_id=graph.graph_id,
            name=graph.name,
            created_at=graph.created_at,
            nodes=[n.name for n in graph.nodes.values()],
            entry_point=graph.entry_point
        )
    
    except Exception as e:
        logger.error(f"Failed to create graph: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/graph/{graph_id}")
async def get_graph(graph_id: str):
    """
    Get graph information.
    
    Args:
        graph_id: The graph ID
    
    Returns:
        Graph information and structure
    """
    graph = graph_store.get(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    return {
        "graph_id": graph.graph_id,
        "name": graph.name,
        "created_at": graph.created_at,
        "nodes": [n.name for n in graph.nodes.values()],
        "edges": [
            {
                "from": e.from_node,
                "to": e.to_node,
                "description": e.description
            }
            for e in graph.edges
        ],
        "entry_point": graph.entry_point
    }


@app.get("/graphs")
async def list_graphs():
    """List all available graphs."""
    graphs = graph_store.list_all()
    return {
        "count": len(graphs),
        "graphs": [
            {
                "graph_id": g.graph_id,
                "name": g.name,
                "created_at": g.created_at,
                "node_count": len(g.nodes),
                "edge_count": len(g.edges)
            }
            for g in graphs.values()
        ]
    }


# ============================================================================
# Workflow Execution Endpoints
# ============================================================================

@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(request: GraphRunRequest):
    """
    Execute a workflow graph.
    
    Args:
        request: Graph run request with graph_id and initial_state
    
    Returns:
        Execution results with final state and logs
    """
    try:
        # Get graph
        graph = graph_store.get(request.graph_id)
        if not graph:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        # Execute workflow
        executor = WorkflowExecutor(graph)
        run = executor.execute(request.initial_state)
        
        # Store run
        run_store.save(run)
        
        # Convert logs to response format
        log_entries = [
            ExecutionLogEntry(
                step_id=log.step_id,
                node_name=log.node_name,
                timestamp=log.timestamp,
                status=log.status,
                error=log.error,
                duration_ms=log.duration_ms
            )
            for log in run.logs
        ]
        
        logger.info(f"Completed graph execution: {run.run_id}")
        
        return GraphRunResponse(
            run_id=run.run_id,
            graph_id=request.graph_id,
            status=run.status.value,
            final_state=run.state,
            visited_nodes=run.visited_nodes,
            logs=log_entries,
            created_at=run.created_at,
            completed_at=run.completed_at,
            error=run.error
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=GraphStateResponse)
async def get_graph_state(run_id: str):
    """
    Get current state of a running workflow.
    
    Args:
        run_id: The workflow run ID
    
    Returns:
        Current state, status, and logs
    """
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    log_entries = [
        ExecutionLogEntry(
            step_id=log.step_id,
            node_name=log.node_name,
            timestamp=log.timestamp,
            status=log.status,
            error=log.error,
            duration_ms=log.duration_ms
        )
        for log in run.logs
    ]
    
    return GraphStateResponse(
        run_id=run.run_id,
        graph_id=run.graph.graph_id,
        status=run.status.value,
        current_state=run.state,
        visited_nodes=run.visited_nodes,
        logs=log_entries
    )


@app.get("/runs")
async def list_runs():
    """List all workflow runs."""
    runs = run_store.list_all()
    return {
        "count": len(runs),
        "runs": [
            {
                "run_id": r.run_id,
                "graph_id": r.graph.graph_id,
                "status": r.status.value,
                "created_at": r.created_at,
                "completed_at": r.completed_at,
                "node_count": len(r.visited_nodes)
            }
            for r in runs.values()
        ]
    }


@app.get("/graph/{graph_id}/runs")
async def list_graph_runs(graph_id: str):
    """List all runs for a specific graph."""
    graph = graph_store.get(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    runs = run_store.list_by_graph(graph_id)
    return {
        "count": len(runs),
        "graph_id": graph_id,
        "runs": [
            {
                "run_id": r.run_id,
                "status": r.status.value,
                "created_at": r.created_at,
                "completed_at": r.completed_at,
                "node_count": len(r.visited_nodes)
            }
            for r in runs.values()
        ]
    }


# ============================================================================
# Tool Management Endpoints
# ============================================================================

@app.get("/tools", response_model=ToolsListResponse)
async def list_tools():
    """List all registered tools."""
    tools_dict = tool_registry.list_tools()
    tools = [
        ToolInfo(name=name, description=desc)
        for name, desc in tools_dict.items()
    ]
    return ToolsListResponse(tools=tools)


# ============================================================================
# Example: Data Quality Pipeline Endpoints
# ============================================================================

@app.post("/workflow/data-quality/run")
async def run_data_quality_workflow(initial_state: Dict[str, Any] = None):
    """
    Run the data quality pipeline workflow with sample data.
    
    Args:
        initial_state: Optional initial state. If not provided, uses sample data.
    
    Returns:
        Execution results
    """
    if initial_state is None:
        initial_state = {
            "data": {
                f"record_{i}": {"value": i * 10, "quality_score": 0.8}
                for i in range(100)
            }
        }
    
    try:
        # Get the pre-registered data quality graph
        graphs = graph_store.list_all()
        dq_graph = None
        for g in graphs.values():
            if g.name == "data_quality_pipeline":
                dq_graph = g
                break
        
        if not dq_graph:
            raise ValueError("Data quality pipeline not found")
        
        # Execute
        executor = WorkflowExecutor(dq_graph)
        run = executor.execute(initial_state)
        
        # Store run
        run_store.save(run)
        
        # Convert logs
        log_entries = [
            ExecutionLogEntry(
                step_id=log.step_id,
                node_name=log.node_name,
                timestamp=log.timestamp,
                status=log.status,
                error=log.error,
                duration_ms=log.duration_ms
            )
            for log in run.logs
        ]
        
        return GraphRunResponse(
            run_id=run.run_id,
            graph_id=dq_graph.graph_id,
            status=run.status.value,
            final_state=run.state,
            visited_nodes=run.visited_nodes,
            logs=log_entries,
            created_at=run.created_at,
            completed_at=run.completed_at,
            error=run.error
        )
    
    except Exception as e:
        logger.error(f"Failed to run data quality workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/data-quality/info")
async def get_data_quality_info():
    """Get information about the data quality pipeline."""
    graphs = graph_store.list_all()
    dq_graph = None
    for g in graphs.values():
        if g.name == "data_quality_pipeline":
            dq_graph = g
            break
    
    if not dq_graph:
        raise HTTPException(status_code=404, detail="Data quality pipeline not found")
    
    return {
        "graph_id": dq_graph.graph_id,
        "name": dq_graph.name,
        "description": "Data Quality Pipeline - Profiles data, identifies anomalies, generates and applies rules",
        "nodes": [n.name for n in dq_graph.nodes.values()],
        "node_count": len(dq_graph.nodes),
        "edges": [
            {
                "from": e.from_node,
                "to": e.to_node,
                "description": e.description
            }
            for e in dq_graph.edges
        ]
    }


# ============================================================================
# Root and Documentation
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Workflow Engine API",
        "version": "1.0.0",
        "description": "A lightweight workflow/graph engine similar to LangGraph",
        "endpoints": {
            "health": "/health",
            "graphs": {
                "create": "POST /graph/create",
                "get": "GET /graph/{graph_id}",
                "list": "GET /graphs"
            },
            "runs": {
                "execute": "POST /graph/run",
                "state": "GET /graph/state/{run_id}",
                "list_all": "GET /runs",
                "list_by_graph": "GET /graph/{graph_id}/runs"
            },
            "tools": {
                "list": "GET /tools"
            },
            "examples": {
                "data_quality_run": "POST /workflow/data-quality/run",
                "data_quality_info": "GET /workflow/data-quality/info"
            },
            "docs": "/docs"
        }
    }
