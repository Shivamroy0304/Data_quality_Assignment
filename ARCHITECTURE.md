# Workflow Engine - Architecture & Design

## System Overview

The Workflow Engine is a Python-based system for defining and executing workflows as directed graphs. It follows a clean, modular architecture with clear separation between the core engine, API layer, and business logic (workflows).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         REST API Endpoints (main.py)                │    │
│  │  /graph/create, /graph/run, /graph/state, /tools   │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐  ┌────▼────┐  ┌────▼──────┐
    │ Storage │  │  Tools  │  │ Workflows │
    │ Layer   │  │Registry │  │           │
    └────┬────┘  └────┬────┘  └────┬──────┘
         │            │            │
    ┌────┴────────────┴────────────┴──────┐
    │                                      │
    │     Core Graph Engine (graph.py)    │
    │                                      │
    │  • Graph - Graph structure           │
    │  • Node - Execution units            │
    │  • Edge - Node connections           │
    │  • WorkflowExecutor - Executor       │
    │  • WorkflowRun - Execution state     │
    │                                      │
    └──────────────────────────────────────┘
```

## Core Components

### 1. Graph Engine (`app/core/graph.py`)

The heart of the system. Provides fundamental graph concepts:

#### Classes:

**Graph**
- Directed acyclic graph of nodes and edges
- Validates structure before execution
- Maintains entry point and node registry

**Node**
- Callable function that takes state and returns updated state
- Can be synchronous or async (extensible)
- Pure functions recommended for predictability

**Edge**
- Connection between two nodes
- Optional condition for conditional routing
- Description for documentation

**WorkflowRun**
- Represents a single execution instance
- Tracks state, status, logs, visited nodes
- Unique run_id for identification

**WorkflowExecutor**
- Executes graphs end-to-end
- Manages node sequencing based on edges
- Handles errors and maintains execution logs
- Prevents infinite loops with iteration limits

#### Key Design Decisions:

- **Functions as nodes**: More flexible than class-based nodes
- **State is a dict**: No schema constraints, highly flexible
- **Conditions are functions**: Easy to compose and test
- **Sequential execution**: Default is linear; can be extended to parallel

### 2. Tool Registry (`app/core/tools.py`)

Manages reusable components that nodes can call:

**ToolRegistry**
- Singleton pattern for global access
- Register tools with name, function, and description
- Tools are first-class citizens in the system

**Usage Pattern:**
```python
registry = get_tool_registry()
registry.register("my_tool", my_function, "Does X")
result = registry.call("my_tool", arg1, arg2)
```

### 3. Storage Layer (`app/core/storage.py`)

Persistent storage for graphs and runs:

**GraphStore**
- In-memory storage for Graph objects
- Can be extended to database

**RunStore**
- In-memory storage for WorkflowRun objects
- Query by run_id or graph_id
- Can be extended to database

#### Extensibility:
```python
# Current: In-memory
# Future: Implement database backend
class GraphStoreDB(GraphStore):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save(self, graph):
        self.db.insert("graphs", graph.to_dict())
```

### 4. API Models (`app/models/schemas.py`)

Pydantic models for type-safe API contracts:

- **GraphCreateRequest/Response**: Graph creation
- **GraphRunRequest/Response**: Workflow execution
- **GraphStateResponse**: Current workflow state
- **ExecutionLogEntry**: Log entry structure

Benefits:
- Automatic validation
- Documentation generation
- Type safety

### 5. API Layer (`app/main.py`)

FastAPI application exposing all functionality:

**Organization:**
- Health checks
- Graph management endpoints
- Execution endpoints
- Tool management
- Example workflow endpoints

**Design Pattern:**
- Dependency injection ready (get_*_store functions)
- RESTful resource modeling
- Comprehensive error handling

### 6. Workflows (`app/workflows/`)

Domain-specific implementations using the engine:

**Data Quality Pipeline**
- 5-step workflow with branching
- Demonstrates state flow, loops, conditions
- Reusable tools for quality checks
- Complete self-contained example

## Data Flow

### Workflow Execution Flow

```
1. API Request: POST /graph/run
   └─> GraphRunRequest(graph_id, initial_state)

2. Graph Retrieval
   └─> GraphStore.get(graph_id)

3. Executor Creation
   └─> WorkflowExecutor(graph)

4. State Initialization
   └─> WorkflowRun(graph, initial_state)

5. Node Execution Loop
   a. Get current node from entry point or edge
   b. Execute node.func(current_state)
   c. Update state with returned dict
   d. Log execution with timestamp and duration
   e. Get next nodes via graph.get_next_nodes()
   f. Repeat until no next nodes or max iterations

6. Completion
   └─> Set status, save run, return results

7. API Response: GraphRunResponse
   └─> Include final_state, logs, visited_nodes
```

### State Transformation

```
Initial State: {"value": 10}
          │
          ▼
    ┌─────────────┐
    │ Node A      │
    │ (multiply)  │
    └──────┬──────┘
           │ Returns: {"value": 20}
           │ State becomes: {"value": 20}
           ▼
    ┌─────────────┐
    │ Node B      │
    │ (add 5)     │
    └──────┬──────┘
           │ Returns: {"value": 25}
           │ State becomes: {"value": 25}
           ▼
    Final State: {"value": 25}
```

## Design Patterns

### 1. Singleton Pattern
```python
# Global registries
_global_registry = None

def get_tool_registry():
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
```

### 2. Registry Pattern
```python
# Tools and nodes are registered and retrieved
registry.register("tool_name", function)
registry.get("tool_name")
```

### 3. Strategy Pattern
```python
# Conditions are strategies for routing
edge.condition = lambda state: state['value'] > 100
```

### 4. Builder Pattern
```python
# Fluent API for graph construction
graph.add_node("step1", func1)
graph.add_edge("step1", "step2")
graph.set_entry_point("step1")
```

### 5. Factory Pattern
```python
# Create workflows
graph = create_data_quality_pipeline()
executor = WorkflowExecutor(graph)
```

## Error Handling Strategy

### Validation Layers

1. **Graph Validation** (before execution)
   - Nodes exist
   - Entry point exists
   - No dangling edges

2. **Node Execution** (during execution)
   - Try/catch around node.func()
   - Log errors with state snapshot
   - Return error status

3. **API Validation** (at entry point)
   - Pydantic model validation
   - Graph exists check
   - Request parameter validation

### Error Recovery

- Failed nodes are logged but don't crash the workflow
- Execution can be inspected via logs
- State snapshot preserved at error point
- Manual retry possible with same graph_id

## Extensibility Points

### 1. Add New Workflow
```python
def create_my_workflow():
    graph = Graph("my_workflow")
    graph.add_node("step1", my_function)
    # ... configure graph
    return graph

# Register in startup
graph_store.save(create_my_workflow())
```

### 2. Add New Tool
```python
def my_tool(arg1, arg2):
    return result

registry = get_tool_registry()
registry.register("my_tool", my_tool, "Description")
```

### 3. Custom Node Logic
```python
def custom_node(state):
    # Access tools
    registry = get_tool_registry()
    result = registry.call("some_tool", state['value'])
    
    # Update and return
    state['result'] = result
    return state

graph.add_node("custom", custom_node)
```

### 4. Database Integration
```python
# Replace in-memory store
class PostgresGraphStore(GraphStore):
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
    
    def save(self, graph):
        # SQL INSERT
        pass
    
    def get(self, graph_id):
        # SQL SELECT
        pass

# In main.py
graph_store = PostgresGraphStore(CONNECTION_STRING)
```

## Performance Considerations

### Current Implementation
- **Node Execution**: Sequential, blocking
- **State Management**: In-memory dictionaries
- **Storage**: In-memory (no persistence)
- **Logging**: Synchronous file operations

### Optimization Opportunities
1. **Async Execution**: Use `asyncio` for I/O-bound nodes
2. **Parallel Nodes**: Execute independent branches in parallel
3. **Caching**: Cache immutable node results
4. **Database**: Use indexed queries for run lookup
5. **Streaming**: WebSocket for real-time log streaming

## Testing Strategy

### Unit Tests
- Individual node functions
- Graph validation logic
- Edge condition evaluation
- Tool registry operations

### Integration Tests
- Full workflow execution
- Conditional branching
- Loop behavior
- Error cases

### Load Tests
- Multiple concurrent executions
- Large state objects
- Deep graphs (many nodes)
- Long-running workflows

## Security Considerations

1. **Input Validation**: All API inputs validated
2. **Code Execution**: Nodes are trusted code (not user-defined)
3. **State Isolation**: Each run has isolated state
4. **Access Control**: Can be added at API layer
5. **Audit Trail**: Complete execution logs for compliance

## Configuration & Deployment

### Environment-based Configuration
```python
# Ready to add environment variables
MAX_ITERATIONS = os.getenv("MAX_ITERATIONS", 1000)
DATABASE_URL = os.getenv("DATABASE_URL", None)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

### Deployment Options
1. **Local Development**: `python run.py`
2. **Docker**: Containerize with Dockerfile
3. **Cloud**: Deploy to AWS Lambda, Google Cloud Run, Azure Functions
4. **Kubernetes**: Helm charts for orchestration

## Future Enhancements

### Short Term
- Database persistence
- WebSocket streaming
- Advanced filtering on list endpoints

### Medium Term
- Async/await support
- Parallel node execution
- Node composition and reusability
- Workflow versioning

### Long Term
- Visual workflow builder
- Distributed execution
- Machine learning integration
- Advanced scheduling and retry logic

## Conclusion

The Workflow Engine provides a clean, extensible foundation for workflow orchestration. Its modular design allows for easy extension while maintaining clarity and simplicity. The codebase prioritizes correctness and clarity over feature complexity, making it suitable for educational purposes and as a foundation for more advanced systems.
