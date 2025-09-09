"""Common node implementations for graph execution."""

from typing import Dict, Any, Callable, List
from .state import StateSchema, AgentState, GraphState
import logging


logger = logging.getLogger(__name__)


def create_input_node(input_key: str = "input") -> Callable[[StateSchema], StateSchema]:
    """Create a node that processes user input."""
    def input_node(state: StateSchema) -> StateSchema:
        user_input = state.get(input_key, "")
        if isinstance(state, AgentState):
            return state.add_message("user", user_input)
        elif isinstance(state, GraphState):
            return state.add_context("user_input", user_input)
        else:
            return state.set("user_input", user_input)
    
    input_node.__name__ = f"input_node_{input_key}"
    return input_node


def create_output_node(output_key: str = "output") -> Callable[[StateSchema], StateSchema]:
    """Create a node that formats output."""
    def output_node(state: StateSchema) -> StateSchema:
        if isinstance(state, AgentState):
            # Get the last assistant message
            assistant_messages = [msg for msg in state.messages if msg["role"] == "assistant"]
            if assistant_messages:
                output = assistant_messages[-1]["content"]
            else:
                output = "No response generated"
        elif isinstance(state, GraphState):
            output = state.context.get("response", "No response generated")
        else:
            output = state.get("response", "No response generated")
        
        return state.set(output_key, output)
    
    output_node.__name__ = f"output_node_{output_key}"
    return output_node


def create_decision_node(
    decision_key: str = "decision",
    condition_func: Callable[[StateSchema], bool] = None
) -> Callable[[StateSchema], StateSchema]:
    """Create a node that makes decisions."""
    def decision_node(state: StateSchema) -> StateSchema:
        if condition_func:
            decision = condition_func(state)
        else:
            # Default decision: check if we have a response
            decision = bool(state.get("response", False))
        
        return state.set(decision_key, decision)
    
    decision_node.__name__ = f"decision_node_{decision_key}"
    return decision_node


def create_tool_call_node(
    tool_name: str,
    tool_func: Callable[[Dict[str, Any]], Any],
    args_extractor: Callable[[StateSchema], Dict[str, Any]] = None
) -> Callable[[StateSchema], StateSchema]:
    """Create a node that calls a tool."""
    def tool_call_node(state: StateSchema) -> StateSchema:
        if args_extractor:
            tool_args = args_extractor(state)
        else:
            tool_args = state.get("tool_args", {})
        
        try:
            result = tool_func(**tool_args)
            logger.info(f"Tool '{tool_name}' executed successfully")
            
            if isinstance(state, AgentState):
                return state.add_intermediate_step({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
            else:
                return state.set(f"{tool_name}_result", result)
        
        except Exception as e:
            logger.error(f"Tool '{tool_name}' failed: {e}")
            error_result = f"Error: {str(e)}"
            
            if isinstance(state, AgentState):
                return state.add_intermediate_step({
                    "tool": tool_name,
                    "args": tool_args,
                    "error": error_result
                })
            else:
                return state.set(f"{tool_name}_error", error_result)
    
    tool_call_node.__name__ = f"tool_call_node_{tool_name}"
    return tool_call_node


def create_conditional_node(
    condition_func: Callable[[StateSchema], bool],
    true_path: str,
    false_path: str
) -> Callable[[StateSchema], StateSchema]:
    """Create a node that sets the next node based on condition."""
    def conditional_node(state: StateSchema) -> StateSchema:
        if isinstance(state, GraphState):
            next_node = true_path if condition_func(state) else false_path
            return state.set_next_node(next_node)
        else:
            next_node = true_path if condition_func(state) else false_path
            return state.set("next_node", next_node)
    
    conditional_node.__name__ = f"conditional_node_{true_path}_or_{false_path}"
    return conditional_node


# Pre-built tool functions
def calculator_tool(expression: str) -> float:
    """Simple calculator tool."""
    try:
        # Safe evaluation of mathematical expressions
        allowed_names = {}
        code = compile(expression, "<string>", "eval")
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return float(result)
    except Exception as e:
        raise ValueError(f"Cannot evaluate expression '{expression}': {e}")


def weather_tool(location: str) -> str:
    """Mock weather tool."""
    weather_data = {
        "beijing": "Sunny, 25°C",
        "shanghai": "Cloudy, 22°C",
        "guangzhou": "Rainy, 28°C",
        "shenzhen": "Sunny, 30°C"
    }
    return weather_data.get(location.lower(), f"Weather data not available for {location}")


def search_tool(query: str) -> List[str]:
    """Mock search tool."""
    # Mock search results
    return [
        f"Search result 1 for: {query}",
        f"Search result 2 for: {query}",
        f"Search result 3 for: {query}"
    ]


# Common node functions
def log_node(node_name: str = "log") -> Callable[[StateSchema], StateSchema]:
    """Create a node that logs the current state."""
    def log_state(state: StateSchema) -> StateSchema:
        logger.info(f"State at {node_name}: {state}")
        return state
    return log_state


def validate_node(validation_func: Callable[[StateSchema], bool]) -> Callable[[StateSchema], StateSchema]:
    """Create a node that validates state."""
    def validate_state(state: StateSchema) -> StateSchema:
        is_valid = validation_func(state)
        return state.set("is_valid", is_valid)
    return validate_state


def transform_node(transform_func: Callable[[StateSchema], Dict[str, Any]]) -> Callable[[StateSchema], StateSchema]:
    """Create a node that transforms state."""
    def transform_state(state: StateSchema) -> StateSchema:
        transformed_data = transform_func(state)
        return state.update(**transformed_data)
    return transform_state