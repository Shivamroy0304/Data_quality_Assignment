# API Reference Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API has no authentication. Authentication can be added using FastAPI's security utilities.

## Response Format
All successful responses return JSON with appropriate HTTP status codes:
- `200 OK`: Successful GET/POST
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Common Response Patterns

### Success Response
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Endpoints Reference

### Health Check

#### `GET /health`
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-11T10:30:00"
}
```

---

### Root / Info

#### `GET /`
Get API overview and available endpoints.

**Response:**
```json
{
  "name": "Workflow Engine API",
  "version": "1.0.0",
  "description": "A lightweight workflow/graph engine similar to LangGraph",
  "endpoints": {
    "health": "/health",
    "graphs": { ... },
    "runs": { ... },
    "tools": { ... },
    "examples": { ... },
    "docs": "/docs"
  }
}
```

---

## Graph Management

### Create Graph

#### `POST /graph/create`
Create a new workflow graph with nodes and edges.

**Request Body:**
```json
{
  "name": "my_workflow",
  "entry_point": "node1",
  "nodes": [
    {
      "name": "node1",
      "description": "First node"
    },
    {
      "name": "node2",
      "description": "Second node"
    }
  ],
  "edges": [
    {
      "from_node": "node1",
      "to_node": "node2",
      "description": "Connection from node1 to node2"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my_workflow",
  "created_at": "2024-12-11T10:30:00",
  "nodes": ["node1", "node2"],
  "entry_point": "node1"
}
```

**Errors:**
- `400`: Invalid graph structure (missing nodes, invalid entry point, etc.)

---

### Get Graph

#### `GET /graph/{graph_id}`
Retrieve details of a specific graph.

**Path Parameters:**
- `graph_id`: The ID of the graph (UUID string)

**Response:**
```json
{
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my_workflow",
  "created_at": "2024-12-11T10:30:00",
  "nodes": ["node1", "node2"],
  "edges": [
    {
      "from": "node1",
      "to": "node2",
      "description": "Connection from node1 to node2"
    }
  ],
  "entry_point": "node1"
}
```

**Errors:**
- `404`: Graph not found

---

### List All Graphs

#### `GET /graphs`
Get a list of all available graphs.

**Response:**
```json
{
  "count": 2,
  "graphs": [
    {
      "graph_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "my_workflow",
      "created_at": "2024-12-11T10:30:00",
      "node_count": 2,
      "edge_count": 1
    },
    {
      "graph_id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "another_workflow",
      "created_at": "2024-12-11T10:35:00",
      "node_count": 3,
      "edge_count": 2
    }
  ]
}
```

---

## Workflow Execution

### Execute Graph

#### `POST /graph/run`
Execute a workflow graph with an initial state.

**Request Body:**
```json
{
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "initial_state": {
    "key1": "value1",
    "key2": 42,
    "key3": ["item1", "item2"]
  }
}
```

**Response (200 OK):**
```json
{
  "run_id": "660e8400-e29b-41d4-a716-446655440001",
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "final_state": {
    "key1": "value1",
    "key2": 42,
    "key3": ["item1", "item2"],
    "processed_by": ["node1", "node2"],
    "result": "success"
  },
  "visited_nodes": ["node1", "node2"],
  "logs": [
    {
      "step_id": "step-uuid-1",
      "node_name": "node1",
      "timestamp": "2024-12-11T10:30:00",
      "status": "success",
      "duration_ms": 15.5,
      "error": null
    },
    {
      "step_id": "step-uuid-2",
      "node_name": "node2",
      "timestamp": "2024-12-11T10:30:01",
      "status": "success",
      "duration_ms": 25.3,
      "error": null
    }
  ],
  "created_at": "2024-12-11T10:30:00",
  "completed_at": "2024-12-11T10:30:02",
  "error": null
}
```

**Status Values:**
- `"completed"`: Workflow completed successfully
- `"failed"`: Workflow failed with an error
- `"running"`: Workflow is still running (for async operations)
- `"paused"`: Workflow is paused

**Errors:**
- `400`: Invalid graph_id or initial_state
- `404`: Graph not found
- `500`: Execution error (will include error message)

---

### Get Workflow State

#### `GET /graph/state/{run_id}`
Get the current state of a running or completed workflow.

**Path Parameters:**
- `run_id`: The ID of the workflow run (UUID string)

**Response:**
```json
{
  "run_id": "660e8400-e29b-41d4-a716-446655440001",
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "current_state": {
    "key1": "value1",
    "key2": 42,
    "processed_by": ["node1", "node2"],
    "result": "success"
  },
  "visited_nodes": ["node1", "node2"],
  "logs": [
    {
      "step_id": "step-uuid-1",
      "node_name": "node1",
      "timestamp": "2024-12-11T10:30:00",
      "status": "success",
      "duration_ms": 15.5,
      "error": null
    }
  ]
}
```

**Errors:**
- `404`: Run not found

---

### List All Runs

#### `GET /runs`
Get a list of all workflow runs across all graphs.

**Response:**
```json
{
  "count": 3,
  "runs": [
    {
      "run_id": "660e8400-e29b-41d4-a716-446655440001",
      "graph_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_at": "2024-12-11T10:30:00",
      "completed_at": "2024-12-11T10:30:02",
      "node_count": 2
    },
    {
      "run_id": "770e8400-e29b-41d4-a716-446655440002",
      "graph_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "failed",
      "created_at": "2024-12-11T10:35:00",
      "completed_at": "2024-12-11T10:35:05",
      "node_count": 1
    }
  ]
}
```

---

### List Runs for Specific Graph

#### `GET /graph/{graph_id}/runs`
Get all runs for a specific graph.

**Path Parameters:**
- `graph_id`: The ID of the graph (UUID string)

**Response:**
```json
{
  "count": 2,
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "runs": [
    {
      "run_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "completed",
      "created_at": "2024-12-11T10:30:00",
      "completed_at": "2024-12-11T10:30:02",
      "node_count": 2
    }
  ]
}
```

**Errors:**
- `404`: Graph not found

---

## Tool Management

### List Available Tools

#### `GET /tools`
Get a list of all registered tools available for use in workflows.

**Response:**
```json
{
  "tools": [
    {
      "name": "profile_data",
      "description": "Profile the dataset to gather statistics"
    },
    {
      "name": "identify_anomalies",
      "description": "Identify data quality anomalies"
    },
    {
      "name": "generate_rules",
      "description": "Generate data quality rules based on anomalies"
    },
    {
      "name": "apply_rules",
      "description": "Apply generated rules to fix quality issues"
    }
  ]
}
```

---

## Data Quality Pipeline (Example Workflow)

### Get Data Quality Pipeline Info

#### `GET /workflow/data-quality/info`
Get information about the pre-built data quality pipeline workflow.

**Response:**
```json
{
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "data_quality_pipeline",
  "description": "Data Quality Pipeline - Profiles data, identifies anomalies, generates and applies rules",
  "nodes": ["profile", "identify_anomalies", "generate_rules", "apply_rules", "summarize"],
  "node_count": 5,
  "edges": [
    {
      "from": "profile",
      "to": "identify_anomalies",
      "description": "Always proceed to anomaly detection"
    },
    {
      "from": "identify_anomalies",
      "to": "generate_rules",
      "description": "Always proceed to rule generation"
    },
    {
      "from": "generate_rules",
      "to": "apply_rules",
      "description": "Always proceed to rule application"
    },
    {
      "from": "apply_rules",
      "to": "profile",
      "description": "Loop back if anomalies remain and not exceeded max iterations"
    },
    {
      "from": "apply_rules",
      "to": "summarize",
      "description": "Proceed to summary when quality goals are met"
    }
  ]
}
```

---

### Run Data Quality Pipeline

#### `POST /workflow/data-quality/run`
Execute the data quality pipeline with optional custom data.

**Request Body (optional):**
```json
{
  "data": {
    "record_1": {"value": 100, "status": "active"},
    "record_2": {"value": 200, "status": "inactive"}
  }
}
```

If not provided, sample data with 100 records is generated automatically.

**Response (200 OK):**
```json
{
  "run_id": "660e8400-e29b-41d4-a716-446655440001",
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "final_state": {
    "data": { ... },
    "profile": {
      "record_count": 100,
      "null_count": 5,
      "field_count": 10,
      "profile_complete": true
    },
    "anomalies": [
      {
        "type": "high_null_count",
        "severity": "warning",
        "count": 5
      },
      {
        "type": "out_of_range_values",
        "severity": "error",
        "count": 3
      }
    ],
    "anomaly_count": 2,
    "rules": [
      {
        "id": "rule_null_check",
        "description": "Null values should be < 10% of records",
        "check_function": "check_null_count"
      },
      {
        "id": "rule_range_check",
        "description": "Values must be within expected range",
        "check_function": "check_value_range"
      }
    ],
    "rules_applied": 2,
    "anomalies_fixed": 2,
    "summary": {
      "total_iterations": 2,
      "final_anomaly_count": 1,
      "total_rules_applied": 4,
      "final_anomalies_fixed": 4
    }
  },
  "visited_nodes": [
    "profile",
    "identify_anomalies",
    "generate_rules",
    "apply_rules",
    "profile",
    "identify_anomalies",
    "generate_rules",
    "apply_rules",
    "summarize"
  ],
  "logs": [
    {
      "step_id": "step-uuid-1",
      "node_name": "profile",
      "timestamp": "2024-12-11T10:30:00",
      "status": "success",
      "duration_ms": 10.5,
      "error": null
    },
    {
      "step_id": "step-uuid-2",
      "node_name": "identify_anomalies",
      "timestamp": "2024-12-11T10:30:01",
      "status": "success",
      "duration_ms": 8.3,
      "error": null
    }
  ],
  "created_at": "2024-12-11T10:30:00",
  "completed_at": "2024-12-11T10:30:05",
  "error": null
}
```

---

## Example Requests (cURL)

### Create a Graph
```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_workflow",
    "entry_point": "step_1",
    "nodes": [
      {"name": "step_1", "description": "First step"},
      {"name": "step_2", "description": "Second step"}
    ],
    "edges": [
      {"from_node": "step_1", "to_node": "step_2"}
    ]
  }'
```

### Run a Graph
```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "550e8400-e29b-41d4-a716-446655440000",
    "initial_state": {"counter": 0}
  }'
```

### Get Workflow State
```bash
curl -X GET "http://localhost:8000/graph/state/660e8400-e29b-41d4-a716-446655440001"
```

### List All Graphs
```bash
curl -X GET "http://localhost:8000/graphs"
```

### List Available Tools
```bash
curl -X GET "http://localhost:8000/tools"
```

### Run Data Quality Pipeline
```bash
curl -X POST "http://localhost:8000/workflow/data-quality/run" \
  -H "Content-Type: application/json"
```

---

## Interactive Documentation

Once the server is running, visit:

- **Swagger UI (Interactive API Explorer)**: http://localhost:8000/docs
- **ReDoc (API Documentation)**: http://localhost:8000/redoc

These provide interactive testing of all endpoints with request/response examples.

---

## Data Types & Format

### UUID Format
All IDs are UUID v4 format: `550e8400-e29b-41d4-a716-446655440000`

### DateTime Format
All timestamps are ISO 8601 format: `2024-12-11T10:30:00`

### State Format
State is a JSON object (flat or nested dictionary) that flows through nodes:
```json
{
  "simple_value": 42,
  "string": "text",
  "nested": {
    "key": "value"
  },
  "list": [1, 2, 3],
  "null_value": null,
  "boolean": true
}
```

---

## Rate Limiting & Quotas

Currently, there are no rate limits. Rate limiting can be added using FastAPI middleware:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## Pagination

List endpoints don't currently support pagination. Pagination can be added to `/graphs` and `/runs` endpoints:

```python
@app.get("/graphs")
async def list_graphs(skip: int = 0, limit: int = 10):
    # Implement offset/limit pagination
    pass
```

---

## Troubleshooting

### Graph Not Found
**Error:** `404 - Graph not found`
**Solution:** Verify the graph_id is correct using `GET /graphs`

### Invalid Graph Structure
**Error:** `400 - Invalid graph: ...`
**Solution:** Check that entry_point exists in nodes list, and all edges reference valid nodes

### Execution Failed
**Error:** `500 - [error message]`
**Solution:** Check the execution logs using `GET /graph/state/{run_id}` to see which node failed

### Port Already in Use
**Solution:** Run on a different port: `uvicorn app.main:app --port 8001`
