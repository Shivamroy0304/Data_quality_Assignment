"""
Data Quality Pipeline workflow.

A practical workflow that demonstrates the graph engine capabilities:
1. Profile data: Generate statistics about the dataset
2. Identify anomalies: Find data quality issues
3. Generate rules: Create quality rules based on anomalies
4. Apply rules: Enforce rules on the data
5. Loop: Repeat until anomaly count is acceptably low
"""

from typing import Dict, Any, List
from app.core.graph import Graph
from app.core.tools import get_tool_registry
import random
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Data Quality Tools
# ============================================================================

def profile_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Profile the dataset: gather statistics about data quality.
    
    Args:
        state: Workflow state containing 'data' key
    
    Returns:
        Updated state with profiling results
    """
    data = state.get("data", {})
    
    profile = {
        "record_count": len(data),
        "null_count": sum(1 for v in data.values() if v is None),
        "field_count": len(data),
        "profile_complete": True
    }
    
    logger.info(f"Profiled data: {profile}")
    
    return {
        "profile": profile,
        "iteration": state.get("iteration", 0) + 1
    }


def identify_anomalies(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify anomalies in the data based on profile.
    
    Detects issues like:
    - High null count
    - Unexpected data patterns
    - Out-of-range values
    
    Args:
        state: Workflow state with profile data
    
    Returns:
        Updated state with anomalies list
    """
    profile = state.get("profile", {})
    anomalies = []
    
    # Check for high null count
    if profile.get("null_count", 0) > profile.get("record_count", 1) * 0.1:
        anomalies.append({
            "type": "high_null_count",
            "severity": "warning",
            "count": profile.get("null_count", 0)
        })
    
    # Simulate finding additional anomalies
    # In real scenario, this would analyze actual data patterns
    sample_anomalies = [
        {"type": "out_of_range_values", "severity": "error", "count": random.randint(1, 10)},
        {"type": "duplicate_records", "severity": "warning", "count": random.randint(0, 5)},
        {"type": "format_mismatch", "severity": "error", "count": random.randint(0, 3)},
    ]
    
    # Randomly include some anomalies (simulating real data quality issues)
    for anomaly in sample_anomalies:
        if random.random() > 0.5:
            anomalies.append(anomaly)
    
    logger.info(f"Identified {len(anomalies)} anomalies")
    
    return {
        "anomalies": anomalies,
        "anomaly_count": len(anomalies)
    }


def generate_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate data quality rules based on identified anomalies.
    
    Args:
        state: Workflow state with anomalies
    
    Returns:
        Updated state with generated rules
    """
    anomalies = state.get("anomalies", [])
    rules = []
    
    for anomaly in anomalies:
        if anomaly["type"] == "high_null_count":
            rules.append({
                "id": "rule_null_check",
                "description": "Null values should be < 10% of records",
                "check_function": "check_null_count"
            })
        elif anomaly["type"] == "out_of_range_values":
            rules.append({
                "id": "rule_range_check",
                "description": "Values must be within expected range",
                "check_function": "check_value_range"
            })
        elif anomaly["type"] == "duplicate_records":
            rules.append({
                "id": "rule_uniqueness",
                "description": "Records should be unique",
                "check_function": "check_uniqueness"
            })
        elif anomaly["type"] == "format_mismatch":
            rules.append({
                "id": "rule_format",
                "description": "Values must match expected format",
                "check_function": "check_format"
            })
    
    logger.info(f"Generated {len(rules)} rules")
    
    return {
        "rules": rules,
        "rule_count": len(rules)
    }


def apply_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply generated rules to fix data quality issues.
    
    Args:
        state: Workflow state with rules
    
    Returns:
        Updated state with application results
    """
    rules = state.get("rules", [])
    applied_count = 0
    fixed_anomalies = 0
    
    for rule in rules:
        # Simulate applying the rule
        # In real scenario, this would actually fix data issues
        applied_count += 1
        # Simulate that applying rules fixes some anomalies
        if random.random() > 0.3:
            fixed_anomalies += 1
    
    logger.info(f"Applied {applied_count} rules, fixed {fixed_anomalies} issues")
    
    return {
        "rules_applied": applied_count,
        "anomalies_fixed": fixed_anomalies
    }


def should_loop(state: Dict[str, Any]) -> bool:
    """
    Determine if we should loop again (continue quality checks).
    
    Stops when:
    - Anomaly count is very low (< 2)
    - Maximum iterations reached (5)
    
    Args:
        state: Workflow state
    
    Returns:
        True if should loop, False otherwise
    """
    iteration = state.get("iteration", 0)
    anomaly_count = state.get("anomaly_count", 0)
    
    should_continue = anomaly_count > 1 and iteration < 5
    logger.info(f"Loop check: iteration={iteration}, anomalies={anomaly_count}, continue={should_continue}")
    
    return should_continue


# ============================================================================
# Register Tools
# ============================================================================

def register_data_quality_tools():
    """Register all data quality tools in the tool registry."""
    registry = get_tool_registry()
    
    registry.register(
        "profile_data",
        profile_data,
        "Profile the dataset to gather statistics"
    )
    registry.register(
        "identify_anomalies",
        identify_anomalies,
        "Identify data quality anomalies"
    )
    registry.register(
        "generate_rules",
        generate_rules,
        "Generate data quality rules based on anomalies"
    )
    registry.register(
        "apply_rules",
        apply_rules,
        "Apply generated rules to fix quality issues"
    )


# ============================================================================
# Create Data Quality Pipeline
# ============================================================================

def create_data_quality_pipeline() -> Graph:
    """
    Create the data quality pipeline workflow.
    
    Workflow steps:
    1. Profile data -> gather statistics
    2. Identify anomalies -> find issues
    3. Generate rules -> create fixes
    4. Apply rules -> implement fixes
    5. Loop back to step 1 if anomalies remain
    
    Returns:
        Configured Graph object
    """
    # Register tools first
    register_data_quality_tools()
    
    # Create graph
    graph = Graph(name="data_quality_pipeline")
    
    # Add nodes that call the tools
    graph.add_node(
        "profile",
        profile_data,
        "Profile the dataset to understand its characteristics"
    )
    graph.add_node(
        "identify_anomalies",
        identify_anomalies,
        "Identify data quality issues and anomalies"
    )
    graph.add_node(
        "generate_rules",
        generate_rules,
        "Generate quality rules based on detected anomalies"
    )
    graph.add_node(
        "apply_rules",
        apply_rules,
        "Apply quality rules to fix issues"
    )
    
    # Add a summary node at the end
    def summarize_results(state: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the quality improvement results."""
        return {
            "summary": {
                "total_iterations": state.get("iteration", 0),
                "final_anomaly_count": state.get("anomaly_count", 0),
                "total_rules_applied": state.get("rules_applied", 0),
                "final_anomalies_fixed": state.get("anomalies_fixed", 0)
            }
        }
    
    graph.add_node(
        "summarize",
        summarize_results,
        "Summarize the results of the quality pipeline"
    )
    
    # Add edges for the workflow
    graph.add_edge("profile", "identify_anomalies", description="Always proceed to anomaly detection")
    graph.add_edge("identify_anomalies", "generate_rules", description="Always proceed to rule generation")
    graph.add_edge("generate_rules", "apply_rules", description="Always proceed to rule application")
    
    # Conditional loop back: if anomalies remain and iteration < 5, loop back to profile
    graph.add_edge(
        "apply_rules",
        "profile",
        condition=should_loop,
        description="Loop back if anomalies remain and not exceeded max iterations"
    )
    
    # Exit condition: if no more anomalies or max iterations reached, go to summary
    graph.add_edge(
        "apply_rules",
        "summarize",
        condition=lambda state: not should_loop(state),
        description="Proceed to summary when quality goals are met"
    )
    
    # Set entry point
    graph.set_entry_point("profile")
    
    return graph
