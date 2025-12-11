"""
Examples of how to extend the Workflow Engine.

This file demonstrates:
1. Creating custom workflows
2. Registering custom tools
3. Using conditional branching
4. Implementing loops
5. Accessing the API programmatically
"""

from app.core.graph import Graph, WorkflowExecutor
from app.core.tools import get_tool_registry
from app.core.storage import get_graph_store
import json


# ===========================================================================
# Example 1: Simple Custom Workflow
# ===========================================================================

def create_simple_workflow():
    """
    Create a simple workflow that processes data through three steps.
    
    Workflow:
    - Extract: Read input data
    - Transform: Process the data
    - Load: Save results
    """
    
    def extract(state):
        """Extract phase: read and validate input."""
        print("EXTRACT: Reading data...")
        return {
            "raw_data": state.get("input_data", []),
            "record_count": len(state.get("input_data", []))
        }
    
    def transform(state):
        """Transform phase: process the data."""
        print("TRANSFORM: Processing data...")
        raw_data = state.get("raw_data", [])
        # Simple transformation: double each value
        transformed = [x * 2 for x in raw_data]
        return {
            "transformed_data": transformed,
            "transformation_complete": True
        }
    
    def load(state):
        """Load phase: prepare results."""
        print("LOAD: Preparing results...")
        return {
            "final_output": {
                "data": state.get("transformed_data", []),
                "status": "success"
            }
        }
    
    # Create graph
    graph = Graph(name="etl_workflow")
    graph.add_node("extract", extract, "Extract data from source")
    graph.add_node("transform", transform, "Transform and process data")
    graph.add_node("load", load, "Load results to output")
    
    # Connect nodes
    graph.add_edge("extract", "transform")
    graph.add_edge("transform", "load")
    
    # Set starting node
    graph.set_entry_point("extract")
    
    return graph


def run_simple_workflow_example():
    """Run the simple workflow example."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple ETL Workflow")
    print("="*60)
    
    graph = create_simple_workflow()
    executor = WorkflowExecutor(graph)
    
    initial_state = {
        "input_data": [1, 2, 3, 4, 5]
    }
    
    run = executor.execute(initial_state)
    
    print(f"\nStatus: {run.status.value}")
    print(f"Final Output: {json.dumps(run.state.get('final_output'), indent=2)}")
    print(f"Execution Log:")
    for log in run.logs:
        print(f"  - {log.node_name}: {log.duration_ms:.2f}ms")


# ===========================================================================
# Example 2: Workflow with Conditional Branching
# ===========================================================================

def create_approval_workflow():
    """
    Create a workflow that routes based on conditions.
    
    Workflow:
    - Check amount
    - If amount > 1000: route to supervisor_approval
    - If amount <= 1000: route to auto_approval
    - Process based on approval
    """
    
    def check_amount(state):
        """Check the request amount."""
        amount = state.get("amount", 0)
        print(f"Checking amount: ${amount}")
        return {"amount_checked": True}
    
    def supervisor_approval(state):
        """Supervisor approves large amounts."""
        print(f"SUPERVISOR: Approving ${state.get('amount')}")
        return {
            "approval_type": "supervisor",
            "approved": True,
            "approval_note": "Approved by supervisor"
        }
    
    def auto_approval(state):
        """Auto-approve small amounts."""
        print(f"AUTO: Approving ${state.get('amount')}")
        return {
            "approval_type": "auto",
            "approved": True,
            "approval_note": "Auto-approved"
        }
    
    def process_approval(state):
        """Process the approved request."""
        approval = state.get("approval_type", "unknown")
        print(f"Processing {approval} approval")
        return {
            "processed": True,
            "result": f"Request processed via {approval} approval"
        }
    
    # Create graph
    graph = Graph(name="approval_workflow")
    graph.add_node("check", check_amount, "Check request amount")
    graph.add_node("supervisor", supervisor_approval, "Supervisor approval path")
    graph.add_node("auto", auto_approval, "Auto approval path")
    graph.add_node("process", process_approval, "Process approved request")
    
    # Add edges with conditions
    # Route to supervisor if amount > 1000
    graph.add_edge(
        "check",
        "supervisor",
        condition=lambda s: s.get("amount", 0) > 1000,
        description="Large amounts need supervisor approval"
    )
    
    # Route to auto approval if amount <= 1000
    graph.add_edge(
        "check",
        "auto",
        condition=lambda s: s.get("amount", 0) <= 1000,
        description="Small amounts auto-approved"
    )
    
    # Both paths converge to process
    graph.add_edge("supervisor", "process")
    graph.add_edge("auto", "process")
    
    graph.set_entry_point("check")
    
    return graph


def run_approval_workflow_example():
    """Run the approval workflow example with different amounts."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Conditional Branching Workflow")
    print("="*60)
    
    graph = create_approval_workflow()
    executor = WorkflowExecutor(graph)
    
    # Test with high amount
    print("\n--- Test 1: High Amount ($5000) ---")
    run = executor.execute({"amount": 5000})
    print(f"Approval Type: {run.state.get('approval_type')}")
    
    # Test with low amount
    print("\n--- Test 2: Low Amount ($500) ---")
    run = executor.execute({"amount": 500})
    print(f"Approval Type: {run.state.get('approval_type')}")


# ===========================================================================
# Example 3: Workflow with Looping
# ===========================================================================

def create_retry_workflow():
    """
    Create a workflow that retries on failure.
    
    Workflow:
    - Attempt task
    - If failed and retries < 3: loop back
    - If succeeded or max retries: end
    """
    
    def attempt_task(state):
        """Attempt the task."""
        attempt = state.get("attempt", 0) + 1
        print(f"Attempting task (attempt {attempt})")
        
        # Simulate occasional failures
        import random
        success = random.random() > 0.5
        
        if success:
            print("✓ Task succeeded!")
            return {
                "attempt": attempt,
                "status": "success"
            }
        else:
            print("✗ Task failed, will retry")
            return {
                "attempt": attempt,
                "status": "failed"
            }
    
    def finalize(state):
        """Finalize the result."""
        attempt = state.get("attempt", 0)
        status = state.get("status", "unknown")
        print(f"Finalized: {status} after {attempt} attempt(s)")
        return {"finalized": True}
    
    # Create graph
    graph = Graph(name="retry_workflow")
    graph.add_node("attempt", attempt_task, "Attempt the task")
    graph.add_node("finalize", finalize, "Finalize results")
    
    # Retry logic: loop back if failed and attempt < 3
    def should_retry(state):
        is_failed = state.get("status") == "failed"
        attempt_count = state.get("attempt", 0)
        should_continue = is_failed and attempt_count < 3
        print(f"Retry check: failed={is_failed}, attempt={attempt_count}, retry={should_continue}")
        return should_continue
    
    graph.add_edge(
        "attempt",
        "attempt",
        condition=should_retry,
        description="Retry if failed and not exceeded max attempts"
    )
    
    graph.add_edge(
        "attempt",
        "finalize",
        condition=lambda s: not should_retry(s),
        description="Proceed to finalize when done"
    )
    
    graph.set_entry_point("attempt")
    
    return graph


def run_retry_workflow_example():
    """Run the retry workflow example."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Looping/Retry Workflow")
    print("="*60)
    
    graph = create_retry_workflow()
    executor = WorkflowExecutor(graph)
    
    run = executor.execute({})
    
    print(f"\nFinal Status: {run.state.get('status')}")
    print(f"Total Attempts: {run.state.get('attempt', 0)}")
    print(f"Nodes Visited: {len(run.visited_nodes)}")


# ===========================================================================
# Example 4: Custom Tools
# ===========================================================================

def register_and_use_tools():
    """Demonstrate tool registration and usage."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Tools")
    print("="*60)
    
    registry = get_tool_registry()
    
    # Register custom tools
    def calculate_total(items):
        """Calculate sum of items."""
        return sum(items)
    
    def apply_discount(total, discount_percent):
        """Apply discount to total."""
        return total * (1 - discount_percent / 100)
    
    registry.register(
        "calculate_total",
        calculate_total,
        "Calculate sum of items"
    )
    
    registry.register(
        "apply_discount",
        apply_discount,
        "Apply percentage discount to amount"
    )
    
    # Now create a workflow that uses these tools
    def process_order(state):
        """Process an order using registered tools."""
        print("Processing order...")
        
        items = state.get("items", [])
        discount = state.get("discount", 0)
        
        # Call tools from the registry
        total = registry.call("calculate_total", items)
        final_price = registry.call("apply_discount", total, discount)
        
        return {
            "subtotal": total,
            "discount_percent": discount,
            "final_price": final_price
        }
    
    graph = Graph(name="order_processing")
    graph.add_node("process", process_order, "Process order with tools")
    graph.set_entry_point("process")
    
    executor = WorkflowExecutor(graph)
    run = executor.execute({
        "items": [10, 20, 30, 40],
        "discount": 10
    })
    
    print(f"\nOrder Summary:")
    print(f"  Subtotal: ${run.state.get('subtotal')}")
    print(f"  Discount: {run.state.get('discount_percent')}%")
    print(f"  Final Price: ${run.state.get('final_price'):.2f}")


# ===========================================================================
# Example 5: Storing and Retrieving Graphs
# ===========================================================================

def store_and_retrieve_example():
    """Demonstrate graph storage and retrieval."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Graph Storage")
    print("="*60)
    
    # Create a graph
    graph = create_simple_workflow()
    
    # Store it
    store = get_graph_store()
    store.save(graph)
    print(f"✓ Stored graph: {graph.graph_id}")
    
    # Retrieve it
    retrieved = store.get(graph.graph_id)
    print(f"✓ Retrieved graph: {retrieved.name}")
    print(f"  Nodes: {[n.name for n in retrieved.nodes.values()]}")
    print(f"  Entry point: {retrieved.entry_point}")


# ===========================================================================
# Main
# ===========================================================================

def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" "*15 + "WORKFLOW ENGINE - EXTENSION EXAMPLES")
    print("="*70)
    
    try:
        # Run examples
        run_simple_workflow_example()
        run_approval_workflow_example()
        run_retry_workflow_example()
        register_and_use_tools()
        store_and_retrieve_example()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY ✓")
        print("="*70)
        
        print("\nKey Takeaways:")
        print("1. Create workflows by building Graphs with nodes and edges")
        print("2. Nodes are Python functions that receive and return state")
        print("3. Use conditions on edges for branching logic")
        print("4. Register tools globally for reuse across workflows")
        print("5. Store graphs and runs for persistence and tracking")
        print("\nFor more information, see:")
        print("- README.md for project overview")
        print("- ARCHITECTURE.md for system design")
        print("- API_REFERENCE.md for API endpoints")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
