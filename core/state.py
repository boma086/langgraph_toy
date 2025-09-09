"""State management system with schema validation."""

from typing import Dict, Any, TypeVar, Generic, Type, get_type_hints, get_origin, get_args
from dataclasses import dataclass, is_dataclass
from copy import deepcopy
import json


T = TypeVar('T')


class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass


class StateSchema:
    """Base class for state schemas with validation."""
    
    def __init__(self, **kwargs):
        """Initialize state with validation."""
        self._validate_types(kwargs)
        self._data = deepcopy(kwargs)
    
    def _validate_types(self, data: Dict[str, Any]) -> None:
        """Validate data types against type hints."""
        type_hints = get_type_hints(self.__class__)
        
        for field, expected_type in type_hints.items():
            if field in data:
                value = data[field]
                if not self._is_valid_type(value, expected_type):
                    raise StateValidationError(
                        f"Field '{field}' expected type {expected_type}, got {type(value)}"
                    )
    
    def _is_valid_type(self, value: Any, expected_type: Type) -> bool:
        """Check if value matches expected type."""
        origin = get_origin(expected_type)
        
        if origin is not None:
            # Handle generic types like Dict[str, Any]
            args = get_args(expected_type)
            if origin is dict:
                return isinstance(value, dict)
            elif origin is list:
                return isinstance(value, list)
        
        return isinstance(value, expected_type)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> 'StateSchema':
        """Create new state with updated value (immutable)."""
        new_data = deepcopy(self._data)
        new_data[key] = value
        
        # Validate the new data
        type_hints = get_type_hints(self.__class__)
        if key in type_hints and not self._is_valid_type(value, type_hints[key]):
            raise StateValidationError(
                f"Field '{key}' expected type {type_hints[key]}, got {type(value)}"
            )
        
        return self.__class__(**new_data)
    
    def update(self, **kwargs) -> 'StateSchema':
        """Create new state with multiple updates (immutable)."""
        new_data = {**self._data, **kwargs}
        return self.__class__(**new_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return deepcopy(self._data)
    
    def to_json(self) -> str:
        """Convert state to JSON string."""
        return json.dumps(self._data, indent=2)
    
    def __eq__(self, other) -> bool:
        """Check equality with another state."""
        if not isinstance(other, self.__class__):
            return False
        return self._data == other._data
    
    def __repr__(self) -> str:
        """String representation of state."""
        return f"{self.__class__.__name__}({self._data})"


class AgentState(StateSchema):
    """State schema for agent operations."""
    
    messages: list
    tool_calls: list
    intermediate_steps: list
    is_complete: bool
    
    def __init__(self, 
                 messages: list = None,
                 tool_calls: list = None,
                 intermediate_steps: list = None,
                 is_complete: bool = False):
        """Initialize agent state."""
        super().__init__(
            messages=messages or [],
            tool_calls=tool_calls or [],
            intermediate_steps=intermediate_steps or [],
            is_complete=is_complete
        )
    
    @property
    def messages(self) -> list:
        """Get messages."""
        return self.get("messages", [])
    
    @property
    def tool_calls(self) -> list:
        """Get tool calls."""
        return self.get("tool_calls", [])
    
    @property
    def intermediate_steps(self) -> list:
        """Get intermediate steps."""
        return self.get("intermediate_steps", [])
    
    @property
    def is_complete(self) -> bool:
        """Get completion status."""
        return self.get("is_complete", False)
    
    def add_message(self, role: str, content: str) -> 'AgentState':
        """Add a message to the state."""
        new_messages = self.messages + [{"role": role, "content": content}]
        return self.update(messages=new_messages)
    
    def add_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> 'AgentState':
        """Add a tool call to the state."""
        new_tool_calls = self.tool_calls + [{"tool": tool_name, "args": tool_args}]
        return self.update(tool_calls=new_tool_calls)
    
    def add_intermediate_step(self, step: Dict[str, Any]) -> 'AgentState':
        """Add an intermediate step to the state."""
        new_steps = self.intermediate_steps + [step]
        return self.update(intermediate_steps=new_steps)


class GraphState(StateSchema):
    """Generic state schema for graph execution."""
    
    current_node: str
    next_node: str
    context: Dict[str, Any]
    results: Dict[str, Any]
    
    def __init__(self,
                 current_node: str = "",
                 next_node: str = "",
                 context: Dict[str, Any] = None,
                 results: Dict[str, Any] = None):
        """Initialize graph state."""
        super().__init__(
            current_node=current_node,
            next_node=next_node,
            context=context or {},
            results=results or {}
        )
    
    @property
    def current_node(self) -> str:
        """Get current node."""
        return self.get("current_node", "")
    
    @property
    def next_node(self) -> str:
        """Get next node."""
        return self.get("next_node", "")
    
    @property
    def context(self) -> Dict[str, Any]:
        """Get context."""
        return self.get("context", {})
    
    @property
    def results(self) -> Dict[str, Any]:
        """Get results."""
        return self.get("results", {})
    
    def set_current_node(self, node_name: str) -> 'GraphState':
        """Set the current node."""
        return self.update(current_node=node_name)
    
    def set_next_node(self, node_name: str) -> 'GraphState':
        """Set the next node."""
        return self.update(next_node=node_name)
    
    def add_context(self, key: str, value: Any) -> 'GraphState':
        """Add context information."""
        new_context = {**self.context, key: value}
        return self.update(context=new_context)
    
    def add_result(self, key: str, value: Any) -> 'GraphState':
        """Add execution result."""
        new_results = {**self.results, key: value}
        return self.update(results=new_results)