#!/usr/bin/env python3
"""
Quick test script to verify the workflow engine without running a server.

This demonstrates:
1. Creating a graph
2. Executing a workflow
3. Checking results and logs
"""

import sys
from app.core.graph import Graph, WorkflowExecutor
from app.workflows.data_quality import create_data_quality_pipeline
import json


def test_basic_graph():
    """Test a simple linear graph."""
    print("\n" + "="*60)
    print("TEST 1: Basic Linear Graph")
    print("="*60)
    
    # Create graph
    graph = Graph(name="test_linear")
    
    def step_1(state):
        print("  Executing Step 1")
        state["step_1_done"] = True
        state["counter"] = state.get("counter", 0) + 1
        return state
    
    def step_2(state):
        print("  Executing Step 2")
        state["step_2_done"] = True
        state["counter"] = state.get("counter", 0) + 10
        return state
    
    def step_3(state):
        print("  Executing Step 3")
        state["step_3_done"] = True
        state["counter"] = state.get("counter", 0) + 100
        return state
    
    # Add nodes
    graph.add_node("step_1", step_1, "First step")
    graph.add_node("step_2", step_2, "Second step")
    graph.add_node("step_3", step_3, "Third step")
    
    # Add edges
    graph.add_edge("step_1", "step_2")
    graph.add_edge("step_2", "step_3")
    
    # Execute
    executor = WorkflowExecutor(graph)
    initial_state = {"start": True}
    run = executor.execute(initial_state)
    
    print(f"\nStatus: {run.status.value}")
    print(f"Visited Nodes: {run.visited_nodes}")
    print(f"Final State: {json.dumps(run.state, indent=2)}")
    print(f"Total Steps: {len(run.logs)}")
    
    assert run.state["counter"] == 111
    assert len(run.visited_nodes) == 3
    print("✓ Test passed!")


def test_conditional_branching():
    """Test graph with conditional routing."""
    print("\n" + "="*60)
    print("TEST 2: Conditional Branching")
    print("="*60)
    
    # Create graph
    graph = Graph(name="test_branching")
    
    def check_value(state):
        print("  Checking value...")
        state["checked"] = True
        return state
    
    def high_path(state):
        print("  Taking HIGH path")
        state["path"] = "high"
        return state
    
    def low_path(state):
        print("  Taking LOW path")
        state["path"] = "low"
        return state
    
    def merge(state):
        print("  Merging results")
        state["merged"] = True
        return state
    
    # Add nodes
    graph.add_node("check", check_value)
    graph.add_node("high", high_path)
    graph.add_node("low", low_path)
    graph.add_node("merge", merge)
    
    # Add edges with conditions
    graph.add_edge("check", "high", condition=lambda s: s.get("value", 0) > 50)
    graph.add_edge("check", "low", condition=lambda s: s.get("value", 0) <= 50)
    graph.add_edge("high", "merge")
    graph.add_edge("low", "merge")
    
    # Test with high value
    executor = WorkflowExecutor(graph)
    run = executor.execute({"value": 75})
    
    print(f"\nWith value=75:")
    print(f"  Path taken: {run.state.get('path')}")
    assert run.state["path"] == "high"
    print("✓ High path test passed!")
    
    # Test with low value
    run = executor.execute({"value": 25})
    print(f"\nWith value=25:")
    print(f"  Path taken: {run.state.get('path')}")
    assert run.state["path"] == "low"
    print("✓ Low path test passed!")


def test_data_quality_pipeline():
    """Test the data quality pipeline workflow."""
    print("\n" + "="*60)
    print("TEST 3: Data Quality Pipeline")
    print("="*60)
    
    # Create the pipeline
    graph = create_data_quality_pipeline()
    
    print(f"Graph: {graph.name}")
    print(f"Nodes: {[n.name for n in graph.nodes.values()]}")
    print(f"Entry point: {graph.entry_point}")
    
    # Execute
    initial_state = {
        "data": {f"record_{i}": {"value": i * 10} for i in range(50)}
    }
    
    executor = WorkflowExecutor(graph)
    run = executor.execute(initial_state)
    
    print(f"\nExecution completed:")
    print(f"  Status: {run.status.value}")
    print(f"  Total iterations: {run.state.get('summary', {}).get('total_iterations', 'N/A')}")
    print(f"  Final anomaly count: {run.state.get('summary', {}).get('final_anomaly_count', 'N/A')}")
    print(f"  Nodes visited: {len(run.visited_nodes)}")
    print(f"  Execution logs: {len(run.logs)}")
    
    # Print sample logs
    print(f"\nExecution trace:")
    for i, log in enumerate(run.logs[:5], 1):
        print(f"  {i}. {log.node_name} - {log.status} ({log.duration_ms:.2f}ms)")
    
    assert run.status.value == "completed"
    assert "summary" in run.state
    print("✓ Data quality pipeline test passed!")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("WORKFLOW ENGINE - INTEGRATION TESTS")
    print("="*60)
    
    try:
        test_basic_graph()
        test_conditional_branching()
        test_data_quality_pipeline()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        print("\nThe workflow engine is working correctly!")
        print("\nTo start the API server, run:")
        print("  python run.py")
        print("\nThen visit:")
        print("  http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
