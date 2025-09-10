"""Agent compiler using decorator pattern - provides LangGraph-like compile() interface."""

from typing import Dict, Any, Optional
from core.execution import ExecutionStrategy, StrategyFactory
from agents.base import BaseAgent
import logging


logger = logging.getLogger(__name__)


class CompiledAgent:
    """A compiled agent wrapper that provides optimized execution.
    
    This is a decorator that wraps any BaseAgent to provide
    compiled execution without modifying the original agent.
    """
    
    def __init__(self, agent: BaseAgent, strategy: ExecutionStrategy):
        """Initialize compiled agent.
        
        Args:
            agent: The original agent to wrap
            strategy: Execution strategy to use
        """
        self._agent = agent
        self._strategy = strategy
        self._compiled_at = None
        logger.info(f"Compiled agent created for {agent.name} using {strategy.__class__.__name__}")
    
    @property
    def name(self) -> str:
        """Get agent name."""
        return self._agent.name
    
    @property
    def tools(self) -> Dict[str, Any]:
        """Get agent tools."""
        return self._agent.tools
    
    def run(self, user_input: str) -> str:
        """Run the compiled agent."""
        logger.debug(f"Executing compiled agent {self.name} with {self._strategy.__class__.__name__}")
        return self._strategy.execute(self._agent, user_input)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "agent_name": self.name,
            "strategy": self._strategy.__class__.__name__,
            "strategy_stats": self._strategy.get_stats(),
            "tools_count": len(self.tools)
        }
    
    def clear_cache(self):
        """Clear strategy cache if applicable."""
        if hasattr(self._strategy, 'clear_cache'):
            self._strategy.clear_cache()
    
    # Delegate to original agent for compatibility
    def register_tool(self, tool) -> None:
        """Register a tool (delegates to original agent)."""
        self._agent.register_tool(tool)
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name (delegates to original agent)."""
        return self._agent.get_tool(name)
    
    def list_tools(self) -> list:
        """List available tools (delegates to original agent)."""
        return self._agent.list_tools()


class AgentCompiler:
    """Compiler for agents - provides LangGraph-like compile() interface.
    
    This class provides a static compile() method similar to LangGraph,
    allowing users to "compile" agents for better performance.
    """
    
    @staticmethod
    def compile(agent: BaseAgent, strategy: str = "compiled") -> CompiledAgent:
        """Compile an agent with specified strategy.
        
        Args:
            agent: The agent to compile
            strategy: Execution strategy ("traditional", "compiled", "auto")
            
        Returns:
            CompiledAgent instance
            
        Example:
            ```python
            # Traditional LangGraph-like usage
            agent = SimpleAgent()
            compiled_agent = AgentCompiler.compile(agent)
            result = compiled_agent.run("Hello")
            
            # Or choose specific strategy
            compiled_agent = AgentCompiler.compile(agent, "traditional")
            ```
        """
        if strategy == "traditional":
            execution_strategy = StrategyFactory.create_traditional()
        elif strategy == "compiled":
            execution_strategy = StrategyFactory.create_compiled()
        elif strategy == "auto":
            execution_strategy = StrategyFactory.create_best_automatic()
        else:
            raise ValueError(f"Unknown strategy: {strategy}. Use 'traditional', 'compiled', or 'auto'")
        
        compiled_agent = CompiledAgent(agent, execution_strategy)
        logger.info(f"Agent {agent.name} compiled with {strategy} strategy")
        
        return compiled_agent
    
    @staticmethod
    def compile_with_cache(agent: BaseAgent, cache_size: int = 50) -> CompiledAgent:
        """Compile an agent with custom cache size.
        
        Args:
            agent: The agent to compile
            cache_size: Maximum number of graphs to cache
            
        Returns:
            CompiledAgent instance with custom cache size
        """
        strategy = StrategyFactory.create_compiled(cache_size)
        return CompiledAgent(agent, strategy)
    
    @staticmethod
    def benchmark(agent: BaseAgent, test_inputs: list = None) -> Dict[str, Any]:
        """Benchmark different execution strategies for an agent.
        
        Args:
            agent: Agent to benchmark
            test_inputs: List of test inputs (default: simple test cases)
            
        Returns:
            Benchmark results comparing different strategies
        """
        if test_inputs is None:
            test_inputs = [
                "Hello, how are you?",
                "What is 2 + 2?",
                "What's the weather like?",
                "Help me calculate 15 * 3"
            ]
        
        strategies = [
            StrategyFactory.create_traditional(),
            StrategyFactory.create_compiled()
        ]
        
        from core.execution import ExecutionBenchmark
        results = ExecutionBenchmark.benchmark(agent, test_inputs, strategies)
        
        logger.info(f"Benchmark completed for {agent.name}")
        return results


# Convenience functions for LangGraph-like experience
def compile(agent: BaseAgent, strategy: str = "compiled") -> CompiledAgent:
    """Convenience function - LangGraph-like compile() experience.
    
    Args:
        agent: Agent to compile
        strategy: Execution strategy name
        
    Returns:
        CompiledAgent instance
        
    Example:
        ```python
        from agents.simple import SimpleAgent
        from core.compilation import compile
        
        agent = SimpleAgent()
        compiled = compile(agent)  # Default: compiled strategy
        result = compiled.run("Hello")
        ```
    """
    return AgentCompiler.compile(agent, strategy)


def compile_with_cache(agent: BaseAgent, cache_size: int = 50) -> CompiledAgent:
    """Convenience function for compilation with custom cache size."""
    return AgentCompiler.compile_with_cache(agent, cache_size)


def get_performance_stats(compiled_agent: CompiledAgent) -> Dict[str, Any]:
    """Get performance statistics for a compiled agent."""
    return compiled_agent.get_stats()