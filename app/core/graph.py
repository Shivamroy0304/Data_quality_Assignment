"""
Core workflow/graph engine implementation.

This module provides the foundation for building workflow systems with:
- Nodes: Functions that process and modify shared state
- Edges: Connections between nodes with optional conditions
- State: Shared dictionary that flows through the workflow
- Branching: Conditional routing based on state
- Looping: Ability to repeat nodes until a condition is met
"""

from typing import Callable, Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """Status of a workflow execution."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ExecutionLog:
    """Log entry for a step execution."""
    step_id: str
    node_name: str
    timestamp: datetime
    status: str
    state_snapshot: Dict[str, Any]
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class NodeDefinition:
    """Definition of a graph node."""
    name: str
    func: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str = ""


@dataclass
class EdgeDefinition:
    """Definition of a graph edge with optional routing condition."""
    from_node: str
    to_node: str
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    description: str = ""


class Graph:
    """
    Represents a directed graph of nodes connected by edges.
    
    Supports:
    - Basic sequential node execution
    - Conditional branching based on state
    - Simple looping (repeat node until condition is met)
    """
    
    def __init__(self, name: str = "default_graph"):
        self.name = name
        self.nodes: Dict[str, NodeDefinition] = {}
        self.edges: List[EdgeDefinition] = []
        self.graph_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.entry_point: Optional[str] = None
    
    def add_node(
        self,
        name: str,
        func: Callable[[Dict[str, Any]], Dict[str, Any]],
        description: str = ""
    ) -> None:
        """
        Add a node to the graph.
        
        Args:
            name: Unique identifier for the node
            func: Function that takes state dict and returns updated state dict
            description: Optional description of what the node does
        """
        if name in self.nodes:
            raise ValueError(f"Node '{name}' already exists")
        
        self.nodes[name] = NodeDefinition(name=name, func=func, description=description)
        
        # Set first added node as entry point if not already set
        if self.entry_point is None:
            self.entry_point = name
    
    def add_edge(
        self,
        from_node: str,
        to_node: str,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        description: str = ""
    ) -> None:
        """
        Add an edge between two nodes.
        
        Args:
            from_node: Source node name
            to_node: Destination node name
            condition: Optional function that takes state and returns True/False
                      for conditional routing. If None, edge is always taken.
            description: Optional description of the edge
        """
        if from_node not in self.nodes:
            raise ValueError(f"Source node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise ValueError(f"Destination node '{to_node}' does not exist")
        
        self.edges.append(EdgeDefinition(
            from_node=from_node,
            to_node=to_node,
            condition=condition,
            description=description
        ))
    
    def set_entry_point(self, node_name: str) -> None:
        """Set the starting node for execution."""
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' does not exist")
        self.entry_point = node_name
    
    def get_next_nodes(self, current_node: str, state: Dict[str, Any]) -> List[str]:
        """
        Get the list of next nodes based on edges and state.
        
        Args:
            current_node: Name of the current node
            state: Current state dictionary
        
        Returns:
            List of node names to execute next
        """
        next_nodes = []
        for edge in self.edges:
            if edge.from_node == current_node:
                # If no condition, always take the edge
                if edge.condition is None:
                    next_nodes.append(edge.to_node)
                # If condition, check if it's met
                elif edge.condition(state):
                    next_nodes.append(edge.to_node)
        
        return next_nodes
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the graph structure.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.nodes:
            return False, "Graph has no nodes"
        
        if self.entry_point is None:
            return False, "No entry point set"
        
        if self.entry_point not in self.nodes:
            return False, f"Entry point '{self.entry_point}' does not exist"
        
        return True, ""


class WorkflowRun:
    """Represents a single execution of a workflow."""
    
    def __init__(self, graph: Graph, initial_state: Dict[str, Any]):
        self.run_id = str(uuid.uuid4())
        self.graph = graph
        self.state = initial_state.copy()
        self.status = ExecutionStatus.RUNNING
        self.logs: List[ExecutionLog] = []
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.visited_nodes: List[str] = []
    
    def get_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return self.state.copy()
    
    def get_logs(self) -> List[ExecutionLog]:
        """Get execution logs."""
        return self.logs.copy()


class WorkflowExecutor:
    """
    Executes a workflow graph with state management and logging.
    
    Supports:
    - Sequential node execution
    - Conditional branching
    - Basic loop detection (to prevent infinite loops)
    """
    
    MAX_ITERATIONS = 1000  # Prevent infinite loops
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.run: Optional[WorkflowRun] = None
    
    def execute(
        self,
        initial_state: Dict[str, Any],
        max_iterations: Optional[int] = None
    ) -> WorkflowRun:
        """
        Execute the workflow from start to finish.
        
        Args:
            initial_state: Initial state dictionary
            max_iterations: Maximum iterations to prevent infinite loops
        
        Returns:
            WorkflowRun object with final state and logs
        """
        # Validate graph
        is_valid, error_msg = self.graph.validate()
        if not is_valid:
            raise ValueError(f"Invalid graph: {error_msg}")
        
        # Initialize run
        self.run = WorkflowRun(self.graph, initial_state)
        max_iterations = max_iterations or self.MAX_ITERATIONS
        iteration = 0
        
        try:
            # Start from entry point
            current_node = self.graph.entry_point
            
            while current_node and iteration < max_iterations:
                iteration += 1
                logger.info(f"[{self.run.run_id}] Executing node: {current_node}")
                
                # Execute the node
                node_def = self.graph.nodes[current_node]
                start_time = datetime.utcnow()
                
                try:
                    # Call node function with current state
                    result = node_def.func(self.run.state)
                    
                    # Update state with result
                    if result and isinstance(result, dict):
                        self.run.state.update(result)
                    
                    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    # Log execution
                    log_entry = ExecutionLog(
                        step_id=str(uuid.uuid4()),
                        node_name=current_node,
                        timestamp=datetime.utcnow(),
                        status="success",
                        state_snapshot=self.run.state.copy(),
                        duration_ms=duration
                    )
                    self.run.logs.append(log_entry)
                    self.run.visited_nodes.append(current_node)
                    
                except Exception as e:
                    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    log_entry = ExecutionLog(
                        step_id=str(uuid.uuid4()),
                        node_name=current_node,
                        timestamp=datetime.utcnow(),
                        status="error",
                        state_snapshot=self.run.state.copy(),
                        error=str(e),
                        duration_ms=duration
                    )
                    self.run.logs.append(log_entry)
                    
                    raise
                
                # Determine next node(s)
                next_nodes = self.graph.get_next_nodes(current_node, self.run.state)
                
                # For simplicity, if multiple next nodes, just pick the first one
                # In a more complex system, you might handle this differently
                current_node = next_nodes[0] if next_nodes else None
            
            if iteration >= max_iterations:
                raise RuntimeError(f"Workflow exceeded maximum iterations ({max_iterations})")
            
            self.run.status = ExecutionStatus.COMPLETED
            self.run.completed_at = datetime.utcnow()
            
        except Exception as e:
            self.run.status = ExecutionStatus.FAILED
            self.run.error = str(e)
            self.run.completed_at = datetime.utcnow()
            logger.error(f"[{self.run.run_id}] Workflow failed: {e}")
            raise
        
        return self.run
    
    def get_current_run(self) -> Optional[WorkflowRun]:
        """Get the current workflow run."""
        return self.run
