"""Tests for state management system."""

import pytest
from core.state import StateSchema, AgentState, GraphState, StateValidationError


class TestStateSchema:
    """Test StateSchema functionality."""
    
    def test_initialization(self):
        """Test state initialization."""
        state = StateSchema(test_key="test_value")
        assert state.get("test_key") == "test_value"
        assert state.get("nonexistent") is None
        assert state.get("nonexistent", "default") == "default"
    
    def test_immutability(self):
        """Test that state updates create new instances."""
        state1 = StateSchema(test_key="original")
        state2 = state1.set("test_key", "modified")
        
        assert state1.get("test_key") == "original"
        assert state2.get("test_key") == "modified"
        assert state1 is not state2
    
    def test_type_validation(self):
        """Test type validation."""
        class TestState(StateSchema):
            name: str
            age: int
        
        # Valid types
        state = TestState(name="John", age=30)
        assert state.get("name") == "John"
        assert state.get("age") == 30
        
        # Invalid types
        with pytest.raises(StateValidationError):
            TestState(name=123, age=30)  # name should be string
        
        with pytest.raises(StateValidationError):
            TestState(name="John", age="thirty")  # age should be int
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        state = StateSchema(name="John", age=30)
        state_dict = state.to_dict()
        
        assert state_dict == {"name": "John", "age": 30}
        assert isinstance(state_dict, dict)
    
    def test_to_json(self):
        """Test JSON conversion."""
        state = StateSchema(name="John", age=30)
        json_str = state.to_json()
        
        assert '"name": "John"' in json_str
        assert '"age": 30' in json_str
        assert isinstance(json_str, str)
    
    def test_equality(self):
        """Test state equality."""
        state1 = StateSchema(name="John", age=30)
        state2 = StateSchema(name="John", age=30)
        state3 = StateSchema(name="Jane", age=25)
        
        assert state1 == state2
        assert state1 != state3
        assert state1 != "not a state"
    
    def test_update_multiple(self):
        """Test updating multiple fields."""
        state1 = StateSchema(name="John", age=30)
        state2 = state1.update(name="Jane", age=25)
        
        assert state1.get("name") == "John"
        assert state1.get("age") == 30
        assert state2.get("name") == "Jane"
        assert state2.get("age") == 25


class TestAgentState:
    """Test AgentState functionality."""
    
    def test_default_initialization(self):
        """Test default agent state."""
        state = AgentState()
        
        assert state.messages == []
        assert state.tool_calls == []
        assert state.intermediate_steps == []
        assert state.is_complete is False
    
    def test_custom_initialization(self):
        """Test custom agent state initialization."""
        messages = [{"role": "user", "content": "Hello"}]
        tool_calls = [{"tool": "calculator", "args": {"expression": "2+2"}}]
        
        state = AgentState(
            messages=messages,
            tool_calls=tool_calls,
            is_complete=True
        )
        
        assert state.messages == messages
        assert state.tool_calls == tool_calls
        assert state.is_complete is True
    
    def test_add_message(self):
        """Test adding messages."""
        state = AgentState()
        new_state = state.add_message("user", "Hello")
        
        assert len(new_state.messages) == 1
        assert new_state.messages[0] == {"role": "user", "content": "Hello"}
        assert state.messages == []  # Original state unchanged
    
    def test_add_tool_call(self):
        """Test adding tool calls."""
        state = AgentState()
        new_state = state.add_tool_call("calculator", {"expression": "2+2"})
        
        assert len(new_state.tool_calls) == 1
        assert new_state.tool_calls[0] == {"tool": "calculator", "args": {"expression": "2+2"}}
        assert state.tool_calls == []  # Original state unchanged
    
    def test_add_intermediate_step(self):
        """Test adding intermediate steps."""
        state = AgentState()
        step = {"tool": "calculator", "result": 4}
        new_state = state.add_intermediate_step(step)
        
        assert len(new_state.intermediate_steps) == 1
        assert new_state.intermediate_steps[0] == step
        assert state.intermediate_steps == []  # Original state unchanged
    
    def test_chained_operations(self):
        """Test chaining multiple operations."""
        state = AgentState()
        
        new_state = (state
                     .add_message("user", "Hello")
                     .add_message("assistant", "Hi there!")
                     .add_tool_call("calculator", {"expression": "2+2"})
                     .add_intermediate_step({"tool": "calculator", "result": 4}))
        
        assert len(new_state.messages) == 2
        assert len(new_state.tool_calls) == 1
        assert len(new_state.intermediate_steps) == 1
        assert new_state.messages[0] == {"role": "user", "content": "Hello"}
        assert new_state.messages[1] == {"role": "assistant", "content": "Hi there!"}


class TestGraphState:
    """Test GraphState functionality."""
    
    def test_default_initialization(self):
        """Test default graph state."""
        state = GraphState()
        
        assert state.current_node == ""
        assert state.next_node == ""
        assert state.context == {}
        assert state.results == {}
    
    def test_custom_initialization(self):
        """Test custom graph state initialization."""
        context = {"user_input": "Hello"}
        results = {"node1": "success"}
        
        state = GraphState(
            current_node="node1",
            next_node="node2",
            context=context,
            results=results
        )
        
        assert state.current_node == "node1"
        assert state.next_node == "node2"
        assert state.context == context
        assert state.results == results
    
    def test_set_current_node(self):
        """Test setting current node."""
        state = GraphState()
        new_state = state.set_current_node("node1")
        
        assert new_state.current_node == "node1"
        assert state.current_node == ""  # Original state unchanged
    
    def test_set_next_node(self):
        """Test setting next node."""
        state = GraphState()
        new_state = state.set_next_node("node2")
        
        assert new_state.next_node == "node2"
        assert state.next_node == ""  # Original state unchanged
    
    def test_add_context(self):
        """Test adding context."""
        state = GraphState()
        new_state = state.add_context("key", "value")
        
        assert new_state.context["key"] == "value"
        assert state.context == {}  # Original state unchanged
    
    def test_add_result(self):
        """Test adding results."""
        state = GraphState()
        new_state = state.add_result("node1", "success")
        
        assert new_state.results["node1"] == "success"
        assert state.results == {}  # Original state unchanged
    
    def test_context_accumulation(self):
        """Test that context accumulates properly."""
        state = GraphState()
        
        new_state = (state
                     .add_context("input", "Hello")
                     .add_context("user", "John")
                     .add_context("session", "123"))
        
        assert new_state.context == {
            "input": "Hello",
            "user": "John",
            "session": "123"
        }
    
    def test_results_accumulation(self):
        """Test that results accumulate properly."""
        state = GraphState()
        
        new_state = (state
                     .add_result("node1", "success")
                     .add_result("node2", "error")
                     .add_result("node3", "completed"))
        
        assert new_state.results == {
            "node1": "success",
            "node2": "error",
            "node3": "completed"
        }