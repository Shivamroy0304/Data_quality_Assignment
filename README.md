# Workflow Engine API

A lightweight, clean implementation of a workflow/graph engine similar to LangGraph. This system allows you to define workflows as directed graphs of nodes (Python functions) connected by edges, with shared state flowing through the execution.

## Project Overview

This is a pure backend implementation demonstrating:
- **Clean Python code structure** with proper separation of concerns
- **Graph/state machine fundamentals** for workflow orchestration
- **FastAPI REST endpoints** for workflow management and execution
- **Tool registry pattern** for extensible workflow components
- **Proper logging and error handling** throughout

## Key Features

### 1. Core Graph Engine (`app/core/graph.py`)
- **Nodes**: Python functions that read and modify shared state
- **Edges**: Connections between nodes with optional conditional routing
- **State Management**: Dictionary-based state flowing through nodes
- **Branching**: Conditional routing based on state values
- **Looping**: Support for repeating nodes until conditions are met
- **Execution Tracking**: Complete logs with timestamps and state snapshots

### 2. Tool Registry (`app/core/tools.py`)
- Register reusable tools (Python functions) globally
- Tools can be called by workflow nodes
- Extensible pattern for adding domain-specific functionality

### 3. FastAPI Endpoints
All endpoints documented and accessible via `/docs` (Swagger UI) when running.

**Graph Management:**
- `POST /graph/create` - Create a new workflow graph
- `GET /graph/{graph_id}` - Get graph details
- `GET /graphs` - List all available graphs

**Execution:**
- `POST /graph/run` - Execute a workflow graph
- `GET /graph/state/{run_id}` - Get current state of a running workflow
- `GET /runs` - List all workflow runs
- `GET /graph/{graph_id}/runs` - List runs for a specific graph

**Tools:**
- `GET /tools` - List available tools and their descriptions

**Data Quality Example:**
- `POST /workflow/data-quality/run` - Run the data quality pipeline
- `GET /workflow/data-quality/info` - Get pipeline information

**Utility:**
- `GET /` - API overview
- `GET /health` - Health check

### 4. Data Quality Pipeline Workflow
A complete example workflow demonstrating all engine features:

1. **Profile** - Gather data statistics
2. **Identify Anomalies** - Detect data quality issues
3. **Generate Rules** - Create quality rules
4. **Apply Rules** - Fix detected issues
5. **Loop** - Repeat until quality goals met
6. **Summarize** - Generate final report

Features conditional branching (loop until anomalies low) and conditional exit.

## Project Structure

```
Tradence/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph.py           # Core graph engine
│   │   ├── tools.py           # Tool registry
│   │   └── storage.py         # In-memory storage for graphs/runs
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models for API
│   └── workflows/
│       ├── __init__.py
│       └── data_quality.py    # Example data quality pipeline
├── run.py                      # Entry point for running the server
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md                   # This file
```

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- pip or conda

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
# Option 1: Using the run script
python run.py

# Option 2: Direct uvicorn command
uvicorn app.main:app --reload

# Option 3: Specify host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Access Documentation

Open your browser and navigate to:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Usage Examples

### Example 1: Run Data Quality Pipeline

```bash
curl -X POST "http://localhost:8000/workflow/data-quality/run" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "record_1": {"value": 100},
      "record_2": {"value": 200}
    }
  }'
```

### Example 2: Create a Custom Graph

```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_workflow",
    "entry_point": "step_1",
    "nodes": [
      {"name": "step_1", "description": "First step"},
      {"name": "step_2", "description": "Second step"},
      {"name": "step_3", "description": "Final step"}
    ],
    "edges": [
      {"from_node": "step_1", "to_node": "step_2"},
      {"from_node": "step_2", "to_node": "step_3"}
    ]
  }'
```

### Example 3: Run a Graph

```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "<graph_id_from_create>",
    "initial_state": {"counter": 0}
  }'
```

### Example 4: Check Workflow Status

```bash
curl -X GET "http://localhost:8000/graph/state/{run_id}"
```

## How the Graph Engine Works

### Core Concepts

1. **State Flow**: Each node receives the current state, processes it, and returns updates
2. **Edges**: Define which node executes next, with optional conditional logic
3. **Execution**: Sequential node execution based on edges and conditions
4. **Logging**: Complete audit trail of execution with state snapshots

### Workflow Execution Flow

```
┌─────────────────┐
│  Initial State  │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ Node 1  │ ──┐
    └─────────┘   │
                  │ (state updated)
         ┌────────┘
         │
         ▼
    ┌─────────┐
    │ Node 2  │ ──┐
    └─────────┘   │
                  │ (state updated)
         ┌────────┘
         │
    ┌────▼────────────┐
    │ Conditional     │
    │ Check           │
    └────┬──────┬─────┘
         │      │
      YES│      │NO
         │      │
    ┌────▼──┐  ┌─────────────┐
    │Loop   │  │Node 3       │
    │back   │  │(final)      │
    └───┬───┘  └─────────────┘
        │
        └──────► (back to Node 1)
```

## Code Quality & Structure

### Design Patterns Used

1. **Decorator Pattern**: Tool registry for extensibility
2. **Strategy Pattern**: Conditional routing logic in edges
3. **State Pattern**: Node functions that modify and return state
4. **Builder Pattern**: Graph construction with fluent API
5. **Registry Pattern**: Global tool registry for easy access

### Python Best Practices

- **Type Hints**: Comprehensive type annotations throughout
- **Docstrings**: Every class and function documented
- **Error Handling**: Proper exception handling with meaningful messages
- **Logging**: Structured logging for debugging and monitoring
- **Separation of Concerns**: Clear module organization
- **Configuration**: Environment-based settings ready to extend

## What's Implemented

✅ Core graph engine with nodes and edges
✅ State management and flow
✅ Conditional branching
✅ Looping support with iteration tracking
✅ Tool registry for extensibility
✅ FastAPI REST endpoints
✅ In-memory storage (easily extensible to database)
✅ Complete execution logging
✅ Data quality pipeline example
✅ Error handling and validation
✅ API documentation (Swagger/ReDoc)

## What Could Be Improved (with more time)

1. **Database Integration**
   - Replace in-memory storage with SQLite/PostgreSQL
   - Add persistence and query capabilities
   - Implement migrations

2. **Async Execution**
   - Support concurrent node execution where applicable
   - Async versions of node functions
   - Task queue integration (Celery, RQ)

3. **Advanced Features**
   - WebSocket streaming for real-time execution logs
   - Node caching to skip redundant executions
   - Dynamic graph modification during runtime
   - Parametrized nodes for reusability
   - Sub-graph composition

4. **Monitoring & Observability**
   - Prometheus metrics for performance tracking
   - Distributed tracing support (OpenTelemetry)
   - Metrics dashboard
   - Alert system for failed workflows

5. **Enhanced Tool System**
   - Tool versioning and rollback
   - Tool dependencies and requirements
   - Tool validation and type checking at registration

6. **Workflow Features**
   - Parallel execution paths
   - Merge/join operations for convergence
   - Timeout handling per node
   - Rollback/compensation logic
   - Retry policies with backoff

7. **API Enhancements**
   - Pagination for list endpoints
   - Advanced filtering and search
   - Bulk operations
   - Scheduled workflow execution
   - Webhook integration

8. **Testing**
   - Unit tests for each module
   - Integration tests for workflows
   - Load testing
   - Test data generators

## API Response Example

### Data Quality Pipeline Execution

**Request:**
```bash
POST /workflow/data-quality/run
```

**Response:**
```json
{
  "run_id": "abc-123-def",
  "graph_id": "graph-456",
  "status": "completed",
  "final_state": {
    "data": {...},
    "profile": {
      "record_count": 100,
      "null_count": 5,
      "field_count": 10,
      "profile_complete": true
    },
    "anomalies": [...],
    "anomaly_count": 2,
    "rules": [...],
    "rules_applied": 3,
    "anomalies_fixed": 2,
    "summary": {
      "total_iterations": 2,
      "final_anomaly_count": 2,
      "total_rules_applied": 3,
      "final_anomalies_fixed": 2
    }
  },
  "visited_nodes": ["profile", "identify_anomalies", "generate_rules", "apply_rules", "profile", "identify_anomalies", "generate_rules", "apply_rules", "summarize"],
  "logs": [
    {
      "step_id": "step-1",
      "node_name": "profile",
      "timestamp": "2024-12-11T10:30:00",
      "status": "success",
      "duration_ms": 15.5,
      "error": null
    },
    ...
  ],
  "created_at": "2024-12-11T10:30:00",
  "completed_at": "2024-12-11T10:30:02",
  "error": null
}
```

## Testing the API

### Quick Test Script

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Check health
health = requests.get(f"{BASE_URL}/health")
print("Health:", health.json())

# 2. Get available tools
tools = requests.get(f"{BASE_URL}/tools")
print("Tools:", json.dumps(tools.json(), indent=2))

# 3. Get data quality workflow info
dq_info = requests.get(f"{BASE_URL}/workflow/data-quality/info")
print("Data Quality Pipeline:", json.dumps(dq_info.json(), indent=2))

# 4. Run data quality workflow
result = requests.post(f"{BASE_URL}/workflow/data-quality/run")
print("Execution Result:", json.dumps(result.json(), indent=2))

# 5. Check execution state
run_id = result.json()["run_id"]
state = requests.get(f"{BASE_URL}/graph/state/{run_id}")
print("Final State:", json.dumps(state.json(), indent=2))
```

## Technical Decisions

1. **In-Memory Storage**: Chosen for simplicity and ease of testing. Can be replaced with a database layer without changing the API.

2. **Dictionary State**: Simple Python dicts for state allow flexible data structures without schema constraints.

3. **Function-Based Nodes**: Functions as nodes provide flexibility and are easy to test, debug, and compose.

4. **Conditional Edges**: Simple boolean functions for conditions - easy to understand and compose complex routing logic.

5. **Linear Execution Model**: Default single-path execution with conditional branching. Extensible to parallel paths.

6. **Execution Logging**: Complete log trails with state snapshots for debugging and auditing.

## Troubleshooting

### Issue: Port already in use
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

### Issue: Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: ModuleNotFoundError
```bash
# Make sure you're in the project root directory
cd /Users/shivamroy/vsCode/Tradence
python run.py
```

## Future Enhancements

See "What Could Be Improved" section above for detailed potential improvements.

## License

This project is provided as-is for educational and evaluation purposes.

## Author

Built as part of the AI Engineering Internship assignment.
