"""Tests for agent functionality."""

import pytest
from agents.simple import SimpleAgent
from agents.base import SimpleTool, ToolResult
from core.state import AgentState


class TestSimpleTool:
    """Test SimpleTool functionality."""
    
    def test_tool_creation(self):
        """Test tool creation."""
        def test_func(x, y):
            return x + y
        
        tool = SimpleTool("test_tool", "Test tool description", test_func)
        
        assert tool.name == "test_tool"
        assert tool.description == "Test tool description"
        assert tool._func == test_func
    
    def test_tool_execution_success(self):
        """Test successful tool execution."""
        def add_func(x, y):
            return x + y
        
        tool = SimpleTool("add", "Add two numbers", add_func)
        result = tool.execute(x=2, y=3)
        
        assert result == 5
    
    def test_tool_execution_error(self):
        """Test tool execution error."""
        def error_func():
            raise ValueError("Tool error")
        
        tool = SimpleTool("error_tool", "Error tool", error_func)
        
        with pytest.raises(ValueError, match="Tool error"):
            tool.execute()


class TestToolResult:
    """Test ToolResult functionality."""
    
    def test_successful_result(self):
        """Test successful tool result."""
        result = ToolResult("test_tool", "success_result")
        
        assert result.tool_name == "test_tool"
        assert result.result == "success_result"
        assert result.error is None
        assert result.is_success() is True
    
    def test_error_result(self):
        """Test error tool result."""
        result = ToolResult("test_tool", None, "error_message")
        
        assert result.tool_name == "test_tool"
        assert result.result is None
        assert result.error == "error_message"
        assert result.is_success() is False
    
    def test_to_dict(self):
        """Test tool result dictionary conversion."""
        result = ToolResult("test_tool", "success_result")
        result_dict = result.to_dict()
        
        assert result_dict == {
            "tool": "test_tool",
            "result": "success_result",
            "error": None
        }


class TestSimpleAgent:
    """Test SimpleAgent functionality."""
    
    def test_agent_creation(self):
        """Test agent creation."""
        agent = SimpleAgent()
        
        assert agent.name == "simple_agent"
        assert len(agent.tools) == 3  # calculator, weather, search
        assert "calculator" in agent.tools
        assert "weather" in agent.tools
        assert "search" in agent.tools
    
    def test_agent_custom_name(self):
        """Test agent with custom name."""
        agent = SimpleAgent("custom_agent")
        
        assert agent.name == "custom_agent"
    
    def test_tool_registration(self):
        """Test tool registration."""
        agent = SimpleAgent()
        
        def test_func():
            return "test"
        
        tool = SimpleTool("test_tool", "Test tool", test_func)
        agent.register_tool(tool)
        
        assert "test_tool" in agent.tools
        assert agent.get_tool("test_tool") == tool
        assert len(agent.list_tools()) == 4
    
    def test_get_nonexistent_tool(self):
        """Test getting nonexistent tool."""
        agent = SimpleAgent()
        
        assert agent.get_tool("nonexistent") is None
    
    def test_should_use_tool(self):
        """Test tool usage detection."""
        agent = SimpleAgent()
        
        # Calculator queries
        assert agent._should_use_tool("calculate 2+2") is True
        assert agent._should_use_tool("what is 5 * 3") is True
        assert agent._should_use_tool("compute 10 / 2") is True
        
        # Weather queries
        assert agent._should_use_tool("weather in beijing") is True
        assert agent._should_use_tool("temperature in shanghai") is True
        
        # Search queries
        assert agent._should_use_tool("search for python") is True
        assert agent._should_use_tool("find information about AI") is True
        
        # Non-tool queries
        assert agent._should_use_tool("hello") is False
        assert agent._should_use_tool("how are you") is False
        assert agent._should_use_tool("what is your name") is False
    
    def test_extract_tool_args_calculator(self):
        """Test extracting calculator arguments."""
        agent = SimpleAgent()
        
        # Various calculator query formats
        test_cases = [
            ("calculate 2+2", {"expression": "2+2"}),
            ("what is 5 * 3", {"expression": "5 * 3"}),
            ("compute 10 / 2", {"expression": "10 / 2"}),
            ("2+2=?", {"expression": "2+2"}),  # Fixed: should be 2+2 not 22
            ("calculate (1 + 2) * 3", {"expression": "(1 + 2) * 3"})  # Fixed: should keep operators
        ]
        
        for query, expected in test_cases:
            args = agent._extract_tool_args(query, "calculator")
            if expected["expression"]:  # Only check if we got a valid expression
                assert "expression" in args
                assert args["expression"] == expected["expression"]
    
    def test_extract_tool_args_weather(self):
        """Test extracting weather arguments."""
        agent = SimpleAgent()
        
        # Various weather query formats
        test_cases = [
            ("weather in beijing", {"location": "beijing"}),
            ("what's the weather in shanghai", {"location": "shanghai"}),
            ("temperature in guangzhou", {"location": "guangzhou"}),
            ("weather shenzhen", {"location": "shenzhen"})
        ]
        
        for query, expected in test_cases:
            args = agent._extract_tool_args(query, "weather")
            assert args == expected
    
    def test_extract_tool_args_search(self):
        """Test extracting search arguments."""
        agent = SimpleAgent()
        
        # Various search query formats
        test_cases = [
            ("search for python programming", {"query": "python programming"}),
            ("search AI information", {"query": "AI information"}),
            ("find details about machine learning", {"query": "details about machine learning"}),
            ("look up python tutorials", {"query": "python tutorials"})
        ]
        
        for query, expected in test_cases:
            args = agent._extract_tool_args(query, "search")
            assert args == expected
    
    def test_choose_tool(self):
        """Test tool selection."""
        agent = SimpleAgent()
        
        # Test calculator selection
        assert agent._choose_tool("calculate 2+2") == "calculator"
        assert agent._choose_tool("what is 5 * 3") == "calculator"
        
        # Test weather selection
        assert agent._choose_tool("weather in beijing") == "weather"
        assert agent._choose_tool("temperature in shanghai") == "weather"
        
        # Test search selection
        assert agent._choose_tool("search for python") == "search"
        assert agent._choose_tool("find information about AI") == "search"
        
        # Test no tool selection
        assert agent._choose_tool("hello") is None
        assert agent._choose_tool("how are you") is None
    
    def test_generate_response_with_tool_results(self):
        """Test response generation with tool results."""
        agent = SimpleAgent()
        
        state = AgentState(
            messages=[{"role": "user", "content": "calculate 2+2"}],
            intermediate_steps=[
                {"tool": "calculator", "result": 4}
            ]
        )
        
        response = agent._generate_response(state)
        assert "Tool result: 4" in response
    
    def test_generate_response_greeting(self):
        """Test response generation for greetings."""
        agent = SimpleAgent()
        
        state = AgentState(
            messages=[{"role": "user", "content": "hello"}]
        )
        
        response = agent._generate_response(state)
        assert "Hello!" in response
        assert "calculations" in response.lower()
        assert "weather" in response.lower()
        assert "search" in response.lower()
    
    def test_generate_response_thanks(self):
        """Test response generation for thanks."""
        agent = SimpleAgent()
        
        state = AgentState(
            messages=[{"role": "user", "content": "thank you"}]
        )
        
        response = agent._generate_response(state)
        assert "You're welcome" in response
    
    def test_generate_response_goodbye(self):
        """Test response generation for goodbye."""
        agent = SimpleAgent()
        
        state = AgentState(
            messages=[{"role": "user", "content": "goodbye"}]
        )
        
        response = agent._generate_response(state)
        assert "Goodbye" in response
    
    def test_should_continue_max_iterations(self):
        """Test continuation check with max iterations."""
        agent = SimpleAgent()
        agent.max_iterations = 2
        
        # Create state with many assistant messages
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "assistant", "content": "How can I help?"}
        ]
        
        state = AgentState(messages=messages)
        assert agent._should_continue(state) is False
    
    def test_should_complete(self):
        """Test completion check."""
        agent = SimpleAgent()
        
        # Completed state
        state = AgentState(is_complete=True)
        assert agent._should_continue(state) is False
        
        # Incomplete state
        state = AgentState(is_complete=False)
        assert agent._should_continue(state) is True
    
    def test_process_input(self):
        """Test input processing."""
        agent = SimpleAgent()
        
        state = agent.process_input("hello world")
        
        assert isinstance(state, AgentState)
        assert len(state.messages) == 1
        assert state.messages[0] == {"role": "user", "content": "hello world"}
    
    def test_format_output(self):
        """Test output formatting."""
        agent = SimpleAgent()
        
        # State with assistant messages
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "Hello there!"}
        ]
        state = AgentState(messages=messages)
        
        output = agent.format_output(state)
        assert output == "Hello there!"
        
        # State without assistant messages
        state = AgentState(messages=[{"role": "user", "content": "hello"}])
        output = agent.format_output(state)
        assert output == "No response generated."
    
    def test_create_graph(self):
        """Test graph creation."""
        agent = SimpleAgent()
        
        graph = agent.create_graph()
        
        assert graph.name == "simple_agent_graph"
        assert len(graph.nodes) == 6  # input, analyze, use_tool, respond, check_complete, output
        assert graph.entry_point == "input"
        assert len(graph.edges) == 7
    
    def test_run_simple_conversation(self):
        """Test running a simple conversation."""
        agent = SimpleAgent()
        
        response = agent.run("hello")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "hello" in response.lower() or "Hello!" in response or "help you" in response.lower()
    
    def test_run_tool_query(self):
        """Test running a tool query."""
        agent = SimpleAgent()
        
        response = agent.run("calculate 2+2")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain tool result information
    
    def test_analyze_input_node(self):
        """Test the analyze input node function."""
        agent = SimpleAgent()
        
        # Test with tool query
        state = AgentState(messages=[{"role": "user", "content": "calculate 2+2"}])
        result_state = agent._analyze_input(state)
        
        assert len(result_state.tool_calls) == 1
        assert result_state.tool_calls[0]["tool"] == "calculator"
        
        # Test without tool query
        state = AgentState(messages=[{"role": "user", "content": "hello"}])
        result_state = agent._analyze_input(state)
        
        assert len(result_state.tool_calls) == 0
    
    def test_use_tool_node(self):
        """Test the use tool node function."""
        agent = SimpleAgent()
        
        # Test with valid tool call
        state = AgentState(tool_calls=[{"tool": "calculator", "args": {"expression": "2+2"}}])
        result_state = agent._use_tool_node(state)
        
        assert len(result_state.intermediate_steps) == 1
        assert result_state.intermediate_steps[0]["tool"] == "calculator"
        assert result_state.intermediate_steps[0]["result"] == 4.0
        
        # Test with invalid tool call
        state = AgentState(tool_calls=[{"tool": "nonexistent", "args": {}}])
        result_state = agent._use_tool_node(state)
        
        # Should not add intermediate steps for invalid tool
        assert len(result_state.intermediate_steps) == 0
    
    def test_respond_node(self):
        """Test the respond node function."""
        agent = SimpleAgent()
        
        state = AgentState(messages=[{"role": "user", "content": "hello"}])
        result_state = agent._respond_node(state)
        
        assert len(result_state.messages) == 2
        assert result_state.messages[1]["role"] == "assistant"
        assert len(result_state.messages[1]["content"]) > 0
    
    def test_check_complete_node(self):
        """Test the check complete node function."""
        agent = SimpleAgent()
        
        # Test incomplete state
        state = AgentState()
        result_state = agent._check_complete_node(state)
        
        assert result_state.is_complete is False
        
        # Test completed state
        state = AgentState(is_complete=True)
        result_state = agent._check_complete_node(state)
        
        assert result_state.is_complete is True