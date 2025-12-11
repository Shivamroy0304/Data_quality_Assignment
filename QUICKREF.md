# Quick Reference Card

## Start the Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload
```

**Server URL:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs`

## Run Tests & Examples
```bash
python test_engine.py    # Run integration tests
python examples.py       # Run extension examples
```

## Common API Calls

### Data Quality Pipeline (Quick Test)
```bash
curl -X POST "http://localhost:8000/workflow/data-quality/run"
```

### Create Graph
```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_workflow",
    "entry_point": "step1",
    "nodes": [{"name": "step1"}, {"name": "step2"}],
    "edges": [{"from_node": "step1", "to_node": "step2"}]
  }'
```

### Run Graph
```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "<id>", "initial_state": {}}'
```

### Check Status
```bash
curl "http://localhost:8000/graph/state/<run_id>"
```

### List All Graphs
```bash
curl "http://localhost:8000/graphs"
```

### List Tools
```bash
curl "http://localhost:8000/tools"
```

## Code Example: Create Workflow

```python
from app.core.graph import Graph, WorkflowExecutor

# Create graph
graph = Graph(name="my_workflow")

# Define nodes
def step1(state):
    return {"processed": True}

def step2(state):
    return {"result": "done"}

# Add nodes
graph.add_node("step1", step1, "First step")
graph.add_node("step2", step2, "Second step")

# Connect nodes
graph.add_edge("step1", "step2")

# Set entry point
graph.set_entry_point("step1")

# Execute
executor = WorkflowExecutor(graph)
run = executor.execute({"input": "data"})

print(f"Status: {run.status.value}")
print(f"Final state: {run.state}")
```

## Code Example: Conditional Branching

```python
# Add conditional edge
graph.add_edge(
    "check",
    "high_path",
    condition=lambda state: state.get("value") > 100
)

graph.add_edge(
    "check",
    "low_path",
    condition=lambda state: state.get("value") <= 100
)
```

## Code Example: Register Tools

```python
from app.core.tools import get_tool_registry

registry = get_tool_registry()

def my_tool(arg1, arg2):
    return arg1 + arg2

registry.register("my_tool", my_tool, "Adds two numbers")

# Use in node
def my_node(state):
    result = registry.call("my_tool", 10, 20)
    return {"result": result}
```

## Project Files

### Core Implementation
- `app/main.py` - FastAPI application
- `app/core/graph.py` - Graph engine (700 lines)
- `app/core/tools.py` - Tool registry
- `app/core/storage.py` - Storage layer
- `app/workflows/data_quality.py` - Example workflow

### Documentation (1000+ lines)
- `README.md` - Main documentation
- `ARCHITECTURE.md` - System design
- `API_REFERENCE.md` - API endpoints
- `DEVELOPMENT.md` - Extension guide
- `SUBMISSION.md` - Submission summary

### Utilities
- `test_engine.py` - Tests
- `examples.py` - Extension examples
- `run.py` - Server entry point
- `Makefile` - Convenience commands
- `quickstart.sh` - Setup script

## Make Commands
```bash
make help      # Show commands
make install   # Install dependencies
make run       # Start server
make test      # Run tests
make clean     # Clean cache
```

## Features Checklist

### Core Engine ✅
- [x] Nodes (Python functions)
- [x] State (Dictionary flow)
- [x] Edges (Connections)
- [x] Conditional branching
- [x] Looping support
- [x] Execution logging
- [x] Error handling

### API Endpoints ✅
- [x] POST /graph/create
- [x] POST /graph/run
- [x] GET /graph/state/{run_id}
- [x] GET /graphs
- [x] GET /tools
- [x] GET /runs
- [x] Example workflows

### Example Workflow ✅
- [x] Data quality pipeline
- [x] Profile → Identify → Generate → Apply → Loop
- [x] Conditional routing
- [x] Tool integration

## Troubleshooting

**Port in use?**
```bash
uvicorn app.main:app --port 8001
```

**Import errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

**Module not found?**
```bash
# Ensure you're in project root
cd /Users/shivamroy/vsCode/Tradence
python run.py
```

## Next Steps

1. ✅ Run tests: `python test_engine.py`
2. ✅ Start server: `python run.py`
3. ✅ Visit docs: `http://localhost:8000/docs`
4. ✅ Try example: `POST /workflow/data-quality/run`
5. ✅ Read: `README.md`, `ARCHITECTURE.md`, `API_REFERENCE.md`

## Key Design Principles

1. **Clean code** - Type hints, docstrings, clear structure
2. **Extensible** - Easy to add workflows, tools, features
3. **Testable** - All components independently testable
4. **Well-documented** - Comprehensive docs at every level
5. **Production-ready** - Proper error handling, logging

---

**Built for:** AI Engineering Internship Assignment
**Date:** December 11, 2024
**Total Files:** 20 files (code, docs, tests, examples)
**Total Lines:** ~3000+ lines of code + documentation
