# Development Guide

This guide explains how to extend and develop the workflow engine.

## Project Structure Quick Reference

```
Tradence/
├── app/
│   ├── core/
│   │   ├── graph.py       # Core classes: Graph, Node, Edge, WorkflowExecutor
│   │   ├── tools.py       # ToolRegistry for tool management
│   │   └── storage.py     # In-memory storage (extendable)
│   ├── models/
│   │   └── schemas.py     # Pydantic models for API validation
│   ├── workflows/
│   │   └── data_quality.py # Example: data quality pipeline
│   └── main.py            # FastAPI application
├── test_engine.py         # Integration tests
├── examples.py            # Extension examples
└── README.md              # Main documentation
```

## Common Development Tasks

### Task 1: Add a New Workflow

**File:** `app/workflows/my_workflow.py`

```python
from app.core.graph import Graph

def create_my_workflow():
    """Create a new workflow."""
    graph = Graph(name="my_workflow")
    
    # Define node functions
    def step_1(state):
        # Process state
        return {"new_key": "new_value"}
    
    def step_2(state):
        # Continue processing
        return {"another_key": state.get("new_key")}
    
    # Add nodes
    graph.add_node("step_1", step_1, "First step")
    graph.add_node("step_2", step_2, "Second step")
    
    # Add edges
    graph.add_edge("step_1", "step_2")
    
    # Set entry point
    graph.set_entry_point("step_1")
    
    return graph
```

**Register in API:** `app/main.py`

```python
@app.on_event("startup")
async def startup_event():
    my_graph = create_my_workflow()
    graph_store.save(my_graph)
```

### Task 2: Create a Custom Tool

**File:** `app/workflows/my_tools.py`

```python
from app.core.tools import get_tool_registry

def register_my_tools():
    """Register custom tools."""
    registry = get_tool_registry()
    
    # Define tool function
    def my_tool(arg1, arg2):
        """Do something useful."""
        return arg1 + arg2
    
    # Register it
    registry.register(
        "my_tool",
        my_tool,
        "Adds two numbers together"
    )

# In workflow node
def node_using_tool(state):
    registry = get_tool_registry()
    result = registry.call("my_tool", 10, 20)
    return {"result": result}
```

### Task 3: Add Database Storage

**File:** `app/core/storage_db.py`

```python
import sqlite3
from app.core.storage import GraphStore
from app.core.graph import Graph
import json

class DatabaseGraphStore(GraphStore):
    """SQLite-backed graph storage."""
    
    def __init__(self, db_path="workflow.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create database tables."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS graphs (
                graph_id TEXT PRIMARY KEY,
                name TEXT,
                data TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save(self, graph: Graph) -> None:
        """Save graph to database."""
        conn = sqlite3.connect(self.db_path)
        # Serialize graph to JSON
        data = {
            "name": graph.name,
            "nodes": {n: node.name for n, node in graph.nodes.items()},
            "edges": [(e.from_node, e.to_node) for e in graph.edges],
            "entry_point": graph.entry_point
        }
        conn.execute(
            "INSERT OR REPLACE INTO graphs VALUES (?, ?, ?, ?)",
            (graph.graph_id, graph.name, json.dumps(data), graph.created_at)
        )
        conn.commit()
        conn.close()
    
    def get(self, graph_id: str) -> Graph:
        """Retrieve graph from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT name, data FROM graphs WHERE graph_id = ?",
            (graph_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        name, data = row
        # Deserialize and reconstruct graph
        graph_data = json.loads(data)
        graph = Graph(name=name)
        graph.graph_id = graph_id
        # ... reconstruct nodes and edges
        return graph
```

**Update main.py:**

```python
from app.core.storage_db import DatabaseGraphStore

graph_store = DatabaseGraphStore(db_path="workflows.db")
```

### Task 4: Add Async Support

**File:** `app/core/async_graph.py`

```python
import asyncio
from app.core.graph import Graph, WorkflowRun, ExecutionStatus
from typing import Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AsyncWorkflowExecutor:
    """Executes workflows with async support."""
    
    async def execute(self, graph: Graph, initial_state: Dict[str, Any]):
        """Execute graph with async node support."""
        run = WorkflowRun(graph, initial_state)
        current_node = graph.entry_point
        
        try:
            while current_node:
                node_def = graph.nodes[current_node]
                
                # Support both sync and async nodes
                if asyncio.iscoroutinefunction(node_def.func):
                    result = await node_def.func(run.state)
                else:
                    result = node_def.func(run.state)
                
                if result:
                    run.state.update(result)
                
                # Get next nodes
                next_nodes = graph.get_next_nodes(current_node, run.state)
                current_node = next_nodes[0] if next_nodes else None
            
            run.status = ExecutionStatus.COMPLETED
        except Exception as e:
            run.status = ExecutionStatus.FAILED
            run.error = str(e)
            logger.error(f"Async execution failed: {e}")
        
        return run
```

### Task 5: Add WebSocket Support

**File:** `app/api/websocket.py`

```python
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json

@app.websocket("/ws/workflow/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    """Stream workflow logs via WebSocket."""
    await websocket.accept()
    
    try:
        run = run_store.get(run_id)
        if not run:
            await websocket.send_json({"error": "Run not found"})
            return
        
        # Send existing logs
        for log in run.logs:
            await websocket.send_json({
                "type": "log",
                "node": log.node_name,
                "status": log.status,
                "duration": log.duration_ms
            })
        
        # Stream new logs as they arrive
        while run.status.value == "running":
            await asyncio.sleep(0.5)
            # Send updated logs
            for new_log in run.logs[len(already_sent):]:
                await websocket.send_json({
                    "type": "log",
                    "node": new_log.node_name,
                    "status": new_log.status
                })
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from run {run_id}")
```

### Task 6: Add Unit Tests

**File:** `tests/test_graph.py`

```python
import pytest
from app.core.graph import Graph, WorkflowExecutor

def test_simple_execution():
    """Test basic graph execution."""
    graph = Graph(name="test")
    
    def node1(state):
        return {"value": 1}
    
    def node2(state):
        return {"value": state["value"] + 1}
    
    graph.add_node("n1", node1)
    graph.add_node("n2", node2)
    graph.add_edge("n1", "n2")
    graph.set_entry_point("n1")
    
    executor = WorkflowExecutor(graph)
    run = executor.execute({})
    
    assert run.state["value"] == 2
    assert len(run.visited_nodes) == 2

def test_conditional_routing():
    """Test branching logic."""
    graph = Graph(name="test_branch")
    
    def check(state):
        return {}
    
    def true_path(state):
        return {"path": "true"}
    
    def false_path(state):
        return {"path": "false"}
    
    graph.add_node("check", check)
    graph.add_node("true", true_path)
    graph.add_node("false", false_path)
    
    graph.add_edge("check", "true", condition=lambda s: s.get("x") > 5)
    graph.add_edge("check", "false", condition=lambda s: s.get("x") <= 5)
    graph.set_entry_point("check")
    
    executor = WorkflowExecutor(graph)
    
    run = executor.execute({"x": 10})
    assert run.state["path"] == "true"
    
    run = executor.execute({"x": 3})
    assert run.state["path"] == "false"

if __name__ == "__main__":
    pytest.main([__file__])
```

**Run tests:**
```bash
pip install pytest
pytest tests/
```

### Task 7: Add API Authentication

**File:** `app/core/auth.py`

```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify API token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    
    # Verify token (simplified)
    valid_tokens = ["secret-token-123"]
    
    if authorization not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return authorization

# In main.py
@app.get("/protected", dependencies=[Depends(verify_token)])
async def protected_endpoint():
    return {"message": "This is protected"}
```

### Task 8: Add Logging Configuration

**File:** `app/config.py`

```python
import logging
import logging.handlers
import os

def setup_logging():
    """Configure logging."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "workflow.log")
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(console_handler)

# In main.py
setup_logging()
```

## Testing Your Changes

### Manual Testing
```bash
# Start server
python run.py

# In another terminal
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/graphs
```

### Programmatic Testing
```python
from app.core.graph import Graph, WorkflowExecutor

graph = Graph("test")
# ... configure graph
executor = WorkflowExecutor(graph)
run = executor.execute({"initial": "state"})

assert run.status.value == "completed"
print(f"Success! Final state: {run.state}")
```

## Code Standards

### Style Guide
- Follow PEP 8
- Use type hints on all functions
- Write docstrings for all public functions/classes
- Use meaningful variable names
- Keep functions small and focused

### Naming Conventions
- `functions_like_this()` - lowercase with underscores
- `ClassName` - PascalCase
- `CONSTANT_VALUE` - UPPERCASE
- `_private_function()` - prefix underscore for private

### Documentation
Every public function should have:
```python
def my_function(param1: str, param2: int) -> dict:
    """
    Brief description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    """
    pass
```

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Workflow State
```python
run = executor.execute(initial_state)
print(json.dumps(run.state, indent=2))
print(f"Visited nodes: {run.visited_nodes}")
for log in run.logs:
    print(f"{log.node_name}: {log.status}")
```

### Check Graph Validity
```python
is_valid, error = graph.validate()
if not is_valid:
    print(f"Graph error: {error}")
```

## Performance Optimization

### Profile Your Workflow
```python
import time

executor = WorkflowExecutor(graph)
start = time.time()
run = executor.execute(initial_state)
duration = time.time() - start

print(f"Total time: {duration:.2f}s")
for log in run.logs:
    print(f"{log.node_name}: {log.duration_ms:.1f}ms")
```

### Optimize Node Functions
- Avoid expensive operations in nodes
- Cache results when possible
- Use appropriate data structures
- Consider async for I/O operations

## Contributing Workflow Improvements

1. Create a new workflow file in `app/workflows/`
2. Implement nodes and register tools as needed
3. Test with `test_engine.py` or `examples.py`
4. Update documentation if adding new features
5. Ensure all code has type hints and docstrings

## Getting Help

- **Graph Concepts**: See `ARCHITECTURE.md`
- **API Usage**: See `API_REFERENCE.md`
- **Examples**: Run `python examples.py`
- **Tests**: Check `test_engine.py`
- **Code**: Read docstrings in source files

---

Happy developing! 🚀
