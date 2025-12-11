"""
Storage layer for graphs and workflow runs.

Currently uses in-memory storage, but can be extended to use a database.
"""

from typing import Dict, Optional
from app.core.graph import Graph, WorkflowRun
import logging

logger = logging.getLogger(__name__)


class GraphStore:
    """In-memory storage for graphs."""
    
    def __init__(self):
        self.graphs: Dict[str, Graph] = {}
    
    def save(self, graph: Graph) -> None:
        """Save a graph."""
        self.graphs[graph.graph_id] = graph
        logger.info(f"Saved graph: {graph.graph_id}")
    
    def get(self, graph_id: str) -> Optional[Graph]:
        """Retrieve a graph by ID."""
        return self.graphs.get(graph_id)
    
    def delete(self, graph_id: str) -> bool:
        """Delete a graph."""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            logger.info(f"Deleted graph: {graph_id}")
            return True
        return False
    
    def list_all(self) -> Dict[str, Graph]:
        """List all graphs."""
        return self.graphs.copy()


class RunStore:
    """In-memory storage for workflow runs."""
    
    def __init__(self):
        self.runs: Dict[str, WorkflowRun] = {}
    
    def save(self, run: WorkflowRun) -> None:
        """Save a workflow run."""
        self.runs[run.run_id] = run
        logger.info(f"Saved run: {run.run_id}")
    
    def get(self, run_id: str) -> Optional[WorkflowRun]:
        """Retrieve a run by ID."""
        return self.runs.get(run_id)
    
    def delete(self, run_id: str) -> bool:
        """Delete a run."""
        if run_id in self.runs:
            del self.runs[run_id]
            logger.info(f"Deleted run: {run_id}")
            return True
        return False
    
    def list_all(self) -> Dict[str, WorkflowRun]:
        """List all runs."""
        return self.runs.copy()
    
    def list_by_graph(self, graph_id: str) -> Dict[str, WorkflowRun]:
        """List all runs for a specific graph."""
        return {
            run_id: run
            for run_id, run in self.runs.items()
            if run.graph.graph_id == graph_id
        }


# Global store instances
_graph_store: Optional[GraphStore] = None
_run_store: Optional[RunStore] = None


def get_graph_store() -> GraphStore:
    """Get the global graph store instance."""
    global _graph_store
    if _graph_store is None:
        _graph_store = GraphStore()
    return _graph_store


def get_run_store() -> RunStore:
    """Get the global run store instance."""
    global _run_store
    if _run_store is None:
        _run_store = RunStore()
    return _run_store
