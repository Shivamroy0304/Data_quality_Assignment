"""
Tool registry for workflow system.

Manages a collection of reusable tools (Python functions) that can be called
from within workflow nodes.
"""

from typing import Callable, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing workflow tools.
    
    Tools are callable functions that can be registered and used by workflow nodes.
    """
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str = ""
    ) -> None:
        """
        Register a tool.
        
        Args:
            name: Unique identifier for the tool
            func: Callable function
            description: Optional description of what the tool does
        """
        if name in self.tools:
            logger.warning(f"Tool '{name}' is being overwritten")
        
        self.tools[name] = func
        self.descriptions[name] = description
        logger.info(f"Registered tool: {name}")
    
    def get(self, name: str) -> Optional[Callable]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
        
        Returns:
            The callable function or None if not found
        """
        return self.tools.get(name)
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """
        Call a registered tool.
        
        Args:
            name: Tool name
            *args: Positional arguments to pass to the tool
            **kwargs: Keyword arguments to pass to the tool
        
        Returns:
            Result from the tool
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        logger.info(f"Calling tool: {name}")
        return self.tools[name](*args, **kwargs)
    
    def list_tools(self) -> Dict[str, str]:
        """
        List all registered tools with their descriptions.
        
        Returns:
            Dictionary of tool names and descriptions
        """
        return self.descriptions.copy()
    
    def exists(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self.tools


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
