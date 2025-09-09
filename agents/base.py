"""Base agent interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from core.state import AgentState, StateSchema
from core.graph import Graph
import logging


logger = logging.getLogger(__name__)


class Tool(ABC):
    """Abstract base class for agent tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        pass


class BaseAgent(ABC):
    """Abstract base class for agents."""
    
    def __init__(self, name: str):
        """Initialize agent."""
        self.name = name
        self.tools: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent."""
        self.tools[tool.name] = tool
        logger.info(f"Tool '{tool.name}' registered for agent '{self.name}'")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return list(self.tools.keys())
    
    @abstractmethod
    def create_graph(self) -> Graph:
        """Create the agent's execution graph."""
        pass
    
    @abstractmethod
    def process_input(self, user_input: str) -> AgentState:
        """Process user input and create initial state."""
        pass
    
    @abstractmethod
    def format_output(self, state: AgentState) -> str:
        """Format the final state for output."""
        pass
    
    def run(self, user_input: str) -> str:
        """Run the agent with user input."""
        # Create initial state
        initial_state = self.process_input(user_input)
        
        # Create and execute graph
        graph = self.create_graph()
        
        # Validate graph
        issues = graph.validate()
        if issues:
            logger.warning(f"Graph validation issues: {issues}")
        
        # Execute graph
        final_state = graph.execute(initial_state)
        
        # Format and return output
        return self.format_output(final_state)


class SimpleTool(Tool):
    """Simple tool implementation."""
    
    def __init__(self, name: str, description: str, func: Callable):
        """Initialize simple tool."""
        self._name = name
        self._description = description
        self._func = func
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool function."""
        try:
            return self._func(**kwargs)
        except Exception as e:
            logger.error(f"Tool '{self.name}' execution failed: {e}")
            raise


class ToolResult:
    """Container for tool execution results."""
    
    def __init__(self, tool_name: str, result: Any, error: str = None):
        """Initialize tool result."""
        self.tool_name = tool_name
        self.result = result
        self.error = error
    
    def is_success(self) -> bool:
        """Check if tool execution was successful."""
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool": self.tool_name,
            "result": self.result,
            "error": self.error
        }


class AgentStep:
    """Container for agent execution steps."""
    
    def __init__(self, step_type: str, content: str, tool_results: List[ToolResult] = None):
        """Initialize agent step."""
        self.step_type = step_type
        self.content = content
        self.tool_results = tool_results or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.step_type,
            "content": self.content,
            "tool_results": [result.to_dict() for result in self.tool_results]
        }