"""Simple reasoning agent implementation."""

import re
from typing import Dict, Any, List, Optional
from .base import BaseAgent, SimpleTool, ToolResult
from core.state import AgentState
from core.graph import Graph
from core.nodes import (
    create_tool_call_node,
    calculator_tool, weather_tool, search_tool
)
from core.edges import (
    has_tool_calls, is_complete, logical_and, logical_not,
    key_equals, string_contains
)
import logging


logger = logging.getLogger(__name__)


class SimpleAgent(BaseAgent):
    """Simple reasoning agent with basic tool usage."""
    
    def __init__(self, name: str = "simple_agent"):
        """Initialize simple agent."""
        super().__init__(name)
        self.max_iterations = 5
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up available tools."""
        # Register basic tools
        self.register_tool(SimpleTool(
            name="calculator",
            description="Calculate mathematical expressions",
            func=calculator_tool
        ))
        
        self.register_tool(SimpleTool(
            name="weather",
            description="Get weather information for a location",
            func=weather_tool
        ))
        
        self.register_tool(SimpleTool(
            name="search",
            description="Search for information",
            func=search_tool
        ))
    
    def _should_use_tool(self, user_input: str) -> bool:
        """Determine if user input requires tool usage."""
        tool_keywords = {
            "calculator": ["calculate", "math", "compute", "+", "-", "*", "/", "="],
            "weather": ["weather", "temperature", "forecast"],
            "search": ["search", "find", "look up", "information about"]
        }
        
        input_lower = user_input.lower()
        
        for tool_name, keywords in tool_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                return True
        
        return False
    
    def _extract_tool_args(self, user_input: str, tool_name: str) -> Dict[str, Any]:
        """Extract tool arguments from user input."""
        if tool_name == "calculator":
            # Extract mathematical expressions
            patterns = [
                r'calculate\s+(.+)',
                r'what\s+is\s+(.+)',
                r'compute\s+(.+)',
                r'(.+)=\?',
                r'(.+)\s*=\s*$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    expr = match.group(1).strip()
                    # Clean up the expression
                    expr = re.sub(r'[^0-9+\-*/().\s]', '', expr)
                    if expr:
                        return {"expression": expr}
        
        elif tool_name == "weather":
            # Extract location
            patterns = [
                r'weather\s+in\s+(.+)',
                r'weather\s+(.+)',
                r'temperature\s+in\s+(.+)',
                r'temperature\s+(.+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    if location:
                        return {"location": location}
        
        elif tool_name == "search":
            # Extract search query
            patterns = [
                r'search\s+for\s+(.+)',
                r'search\s+(.+)',
                r'find\s+(.+)',
                r'look\s+up\s+(.+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                    if query:
                        return {"query": query}
        
        return {}
    
    def _choose_tool(self, user_input: str) -> Optional[str]:
        """Choose appropriate tool based on user input."""
        if self._should_use_tool(user_input):
            input_lower = user_input.lower()
            
            # Priority order for tool selection
            tool_priorities = ["calculator", "weather", "search"]
            
            for tool_name in tool_priorities:
                if tool_name in self.tools:
                    args = self._extract_tool_args(user_input, tool_name)
                    if args:
                        return tool_name
        
        return None
    
    def _generate_response(self, state: AgentState) -> str:
        """Generate response based on current state."""
        # If we have tool results, incorporate them
        if state.intermediate_steps:
            tool_responses = []
            for step in state.intermediate_steps:
                if "result" in step:
                    tool_responses.append(f"Tool result: {step['result']}")
                elif "error" in step:
                    tool_responses.append(f"Tool error: {step['error']}")
            
            if tool_responses:
                return "I've used some tools to help answer your question. " + " ".join(tool_responses)
        
        # Simple response generation based on last message
        if state.messages:
            last_message = state.messages[-1]
            if last_message["role"] == "user":
                user_input = last_message["content"].lower()
                
                # Simple response patterns
                if any(word in user_input for word in ["hello", "hi", "hey"]):
                    return "Hello! I'm a simple agent that can help you with calculations, weather information, and searches. How can I assist you?"
                
                elif any(word in user_input for word in ["thank", "thanks"]):
                    return "You're welcome! Is there anything else I can help you with?"
                
                elif any(word in user_input for word in ["bye", "goodbye"]):
                    return "Goodbye! Feel free to come back if you need help."
                
                elif "?" in user_input:
                    return "I understand you're asking a question. Let me help you with that."
        
        return "I'm processing your request. Please let me know if you need any specific information."
    
    def _should_continue(self, state: AgentState) -> bool:
        """Determine if agent should continue processing."""
        if state.is_complete:
            return False
        
        # Check if we've reached maximum iterations
        message_count = len([msg for msg in state.messages if msg["role"] == "assistant"])
        if message_count >= self.max_iterations:
            return False
        
        # Check if we have a good response
        if state.messages:
            last_message = state.messages[-1]
            if last_message["role"] == "assistant":
                # Simple heuristic: if response is substantial enough, stop
                if len(last_message["content"]) > 50:
                    return False
        
        return True
    
    def create_graph(self) -> Graph:
        """Create the agent's execution graph."""
        from core.graph import Graph
        
        graph = Graph(f"{self.name}_graph")
        
        # Add nodes
        graph.add_node("input", self._create_input_node)
        graph.add_node("analyze", self._analyze_input)
        graph.add_node("use_tool", self._use_tool_node)
        graph.add_node("respond", self._respond_node)
        graph.add_node("check_complete", self._check_complete_node)
        graph.add_node("output", self._create_output_node)
        
        # Add edges
        graph.add_edge("input", "analyze")
        graph.add_edge("analyze", "use_tool", condition=has_tool_calls())
        graph.add_edge("analyze", "respond", condition=logical_not(has_tool_calls()))
        graph.add_edge("use_tool", "respond")
        graph.add_edge("respond", "check_complete")
        graph.add_edge("check_complete", "output", condition=is_complete)
        graph.add_edge("check_complete", "analyze", condition=logical_not(is_complete))
        
        graph.set_entry_point("input")
        
        return graph
    
    def _analyze_input(self, state: AgentState) -> AgentState:
        """Analyze user input and determine if tools are needed."""
        if not state.messages:
            return state
        
        # Get the last user message
        user_messages = [msg for msg in state.messages if msg["role"] == "user"]
        if not user_messages:
            return state
        
        user_input = user_messages[-1]["content"]
        
        # Determine if we need to use tools
        tool_name = self._choose_tool(user_input)
        if tool_name:
            tool_args = self._extract_tool_args(user_input, tool_name)
            if tool_args:
                return state.add_tool_call(tool_name, tool_args)
        
        return state
    
    def _use_tool_node(self, state: AgentState) -> AgentState:
        """Execute tool calls."""
        if not state.tool_calls:
            return state
        
        # Execute the first tool call
        tool_call = state.tool_calls[0]
        tool_name = tool_call["tool"]
        tool_args = tool_call["args"]
        
        if tool_name in self.tools:
            try:
                tool = self.tools[tool_name]
                result = tool.execute(**tool_args)
                return state.add_intermediate_step({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
            except Exception as e:
                return state.add_intermediate_step({
                    "tool": tool_name,
                    "args": tool_args,
                    "error": str(e)
                })
        
        return state
    
    def _respond_node(self, state: AgentState) -> AgentState:
        """Generate response."""
        response = self._generate_response(state)
        return state.add_message("assistant", response)
    
    def _check_complete_node(self, state: AgentState) -> AgentState:
        """Check if processing is complete."""
        should_continue = self._should_continue(state)
        return state.update(is_complete=not should_continue)
    
    def process_input(self, user_input: str) -> AgentState:
        """Process user input and create initial state."""
        return AgentState(messages=[{"role": "user", "content": user_input}])
    
    def _create_input_node(self, state: AgentState) -> AgentState:
        """Create input node that preserves the AgentState as-is."""
        # The user input is already in the messages from process_input, so we don't need to modify the state
        return state
    
    def _create_output_node(self, state: AgentState) -> AgentState:
        """Create output node that preserves the state as-is."""
        # The output is already in the messages, so we don't need to modify the state
        return state
    
    def format_output(self, state: AgentState) -> str:
        """Format the final state for output."""
        # Get the last assistant message
        assistant_messages = [msg for msg in state.messages if msg["role"] == "assistant"]
        if assistant_messages:
            return assistant_messages[-1]["content"]
        
        return "No response generated."