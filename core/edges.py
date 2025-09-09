"""Edge creation utilities and common edge conditions."""

from typing import Callable, Dict, Any, List
from .state import StateSchema, AgentState, GraphState


def always_true(state: StateSchema) -> bool:
    """Edge condition that always returns True."""
    return True


def always_false(state: StateSchema) -> bool:
    """Edge condition that always returns False."""
    return False


def has_key(key: str) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if state has a key."""
    def condition(state: StateSchema) -> bool:
        return key in state.to_dict()
    return condition


def key_equals(key: str, value: Any) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if state key equals value."""
    def condition(state: StateSchema) -> bool:
        return state.get(key) == value
    return condition


def key_exists_and_true(key: str) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if state key exists and is truthy."""
    def condition(state: StateSchema) -> bool:
        return bool(state.get(key, False))
    return condition


def has_messages(min_count: int = 1) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if AgentState has minimum messages."""
    def condition(state: StateSchema) -> bool:
        if isinstance(state, AgentState):
            return len(state.messages) >= min_count
        return False
    return condition


def is_complete(state: StateSchema) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if state is complete."""
    def condition(state: StateSchema) -> bool:
        if isinstance(state, AgentState):
            return state.is_complete
        return state.get("is_complete", False)
    return condition


def has_tool_calls() -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if AgentState has tool calls."""
    def condition(state: StateSchema) -> bool:
        if isinstance(state, AgentState):
            return len(state.tool_calls) > 0
        return False
    return condition


def current_node_equals(node_name: str) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks current node."""
    def condition(state: StateSchema) -> bool:
        if isinstance(state, GraphState):
            return state.current_node == node_name
        return state.get("current_node") == node_name
    return condition


def value_in_list(key: str, valid_values: List[Any]) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if value is in allowed list."""
    def condition(state: StateSchema) -> bool:
        return state.get(key) in valid_values
    return condition


def numeric_condition(key: str, operator: str, value: float) -> Callable[[StateSchema], bool]:
    """Create edge condition for numeric comparisons."""
    def condition(state: StateSchema) -> bool:
        state_value = state.get(key)
        if not isinstance(state_value, (int, float)):
            return False
        
        if operator == ">":
            return state_value > value
        elif operator == ">=":
            return state_value >= value
        elif operator == "<":
            return state_value < value
        elif operator == "<=":
            return state_value <= value
        elif operator == "==":
            return state_value == value
        elif operator == "!=":
            return state_value != value
        else:
            return False
    return condition


def string_contains(key: str, substring: str) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if string contains substring."""
    def condition(state: StateSchema) -> bool:
        state_value = state.get(key)
        if not isinstance(state_value, str):
            return False
        return substring in state_value
    return condition


def string_starts_with(key: str, prefix: str) -> Callable[[StateSchema], bool]:
    """Create edge condition that checks if string starts with prefix."""
    def condition(state: StateSchema) -> bool:
        state_value = state.get(key)
        if not isinstance(state_value, str):
            return False
        return state_value.startswith(prefix)
    return condition


def logical_and(*conditions: Callable[[StateSchema], bool]) -> Callable[[StateSchema], bool]:
    """Create edge condition that combines multiple conditions with AND."""
    def condition(state: StateSchema) -> bool:
        return all(cond(state) for cond in conditions)
    return condition


def logical_or(*conditions: Callable[[StateSchema], bool]) -> Callable[[StateSchema], bool]:
    """Create edge condition that combines multiple conditions with OR."""
    def condition(state: StateSchema) -> bool:
        return any(cond(state) for cond in conditions)
    return condition


def logical_not(condition: Callable[[StateSchema], bool]) -> Callable[[StateSchema], bool]:
    """Create edge condition that negates another condition."""
    def not_condition(state: StateSchema) -> bool:
        return not condition(state)
    return not_condition


class EdgeBuilder:
    """Builder class for creating edges with conditions."""
    
    @staticmethod
    def sequential(source: str, target: str) -> tuple:
        """Create a simple sequential edge."""
        return (source, target, always_true)
    
    @staticmethod
    def conditional(source: str, target: str, condition: Callable[[StateSchema], bool]) -> tuple:
        """Create a conditional edge."""
        return (source, target, condition)
    
    @staticmethod
    def branch(source: str, true_target: str, false_target: str, condition: Callable[[StateSchema], bool]) -> List[tuple]:
        """Create branching edges."""
        return [
            (source, true_target, condition),
            (source, false_target, logical_not(condition))
        ]
    
    @staticmethod
    def switch(source: str, cases: Dict[Any, str], default: str = None) -> List[tuple]:
        """Create switch-like branching edges."""
        edges = []
        for value, target in cases.items():
            edges.append((source, target, key_equals("switch_value", value)))
        
        if default:
            edges.append((source, default, always_true))
        
        return edges