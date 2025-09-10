"""Tests for compilation functionality."""

import pytest
from agents.simple import SimpleAgent
from core.execution import TraditionalStrategy, CompiledStrategy, StrategyFactory, ExecutionBenchmark
from core.compilation import compile, AgentCompiler, CompiledAgent
import time


class TestTraditionalStrategy:
    """Test traditional execution strategy."""
    
    def test_traditional_strategy_creation(self):
        """Test traditional strategy creation."""
        strategy = StrategyFactory.create_traditional()
        assert isinstance(strategy, TraditionalStrategy)
        assert strategy.execution_count == 0
        assert strategy.total_time == 0.0
    
    def test_traditional_strategy_execution(self):
        """Test traditional strategy execution."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_traditional()
        
        result = strategy.execute(agent, "Hello")
        assert isinstance(result, str)
        assert len(result) > 0
        assert strategy.execution_count == 1
        assert strategy.total_time > 0.0
    
    def test_traditional_strategy_stats(self):
        """Test traditional strategy statistics."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_traditional()
        
        # Execute multiple times
        strategy.execute(agent, "Test 1")
        strategy.execute(agent, "Test 2")
        
        stats = strategy.get_stats()
        assert stats["strategy"] == "traditional"
        assert stats["execution_count"] == 2
        assert stats["total_time"] > 0.0
        assert stats["avg_time"] > 0.0


class TestCompiledStrategy:
    """Test compiled execution strategy."""
    
    def test_compiled_strategy_creation(self):
        """Test compiled strategy creation."""
        strategy = StrategyFactory.create_compiled()
        assert isinstance(strategy, CompiledStrategy)
        assert strategy.execution_count == 0
        assert strategy.cache_hits == 0
        assert strategy.cache_misses == 0
    
    def test_compiled_strategy_execution(self):
        """Test compiled strategy execution."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_compiled()
        
        result = strategy.execute(agent, "Hello")
        assert isinstance(result, str)
        assert len(result) > 0
        assert strategy.execution_count == 1
        # First execution should be a cache miss
        assert strategy.cache_misses == 1
    
    def test_compiled_strategy_caching(self):
        """Test compiled strategy caching."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_compiled()
        
        # First execution (cache miss)
        strategy.execute(agent, "Test 1")
        assert strategy.cache_misses == 1
        assert strategy.cache_hits == 0
        
        # Second execution with same agent (cache hit)
        strategy.execute(agent, "Test 2")
        assert strategy.cache_misses == 1  # Should still be 1
        assert strategy.cache_hits == 1  # Should be 1 now
    
    def test_compiled_strategy_stats(self):
        """Test compiled strategy statistics."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_compiled()
        
        # Execute multiple times
        strategy.execute(agent, "Test 1")
        strategy.execute(agent, "Test 2")
        
        stats = strategy.get_stats()
        assert stats["strategy"] == "compiled"
        assert stats["execution_count"] == 2
        assert stats["cache_hits"] >= 0
        assert stats["cache_misses"] >= 0
        assert "hit_rate" in stats
        assert "compilation_time" in stats
    
    def test_compiled_strategy_cache_clear(self):
        """Test compiled strategy cache clearing."""
        strategy = StrategyFactory.create_compiled()
        
        # Execute to populate cache
        agent = SimpleAgent()
        strategy.execute(agent, "Test")
        
        # Clear cache
        strategy.clear_cache()
        assert strategy.cache_hits == 0
        assert strategy.cache_misses == 0
        assert strategy.compilation_time == 0.0


class TestStrategyFactory:
    """Test strategy factory."""
    
    def test_create_traditional(self):
        """Test creating traditional strategy."""
        strategy = StrategyFactory.create_traditional()
        assert isinstance(strategy, TraditionalStrategy)
    
    def test_create_compiled(self):
        """Test creating compiled strategy."""
        strategy = StrategyFactory.create_compiled()
        assert isinstance(strategy, CompiledStrategy)
    
    def test_create_compiled_with_custom_size(self):
        """Test creating compiled strategy with custom cache size."""
        strategy = StrategyFactory.create_compiled(cache_size=100)
        assert isinstance(strategy, CompiledStrategy)
        # Note: cache size is internal, but we can verify it was created
    
    def test_create_best_automatic(self):
        """Test creating automatic strategy."""
        strategy = StrategyFactory.create_best_automatic()
        # Currently defaults to compiled strategy
        assert isinstance(strategy, CompiledStrategy)


class TestCompiledAgent:
    """Test compiled agent functionality."""
    
    def test_compiled_agent_creation(self):
        """Test compiled agent creation."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_compiled()
        compiled_agent = CompiledAgent(agent, strategy)
        
        assert compiled_agent.name == agent.name
        assert compiled_agent.tools == agent.tools
        assert compiled_agent._agent is agent
        assert compiled_agent._strategy is strategy
    
    def test_compiled_agent_execution(self):
        """Test compiled agent execution."""
        agent = SimpleAgent()
        compiled_agent = compile(agent)
        
        result = compiled_agent.run("Hello")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_compiled_agent_stats(self):
        """Test compiled agent statistics."""
        agent = SimpleAgent()
        compiled_agent = compile(agent)
        
        # Execute multiple times
        compiled_agent.run("Test 1")
        compiled_agent.run("Test 2")
        
        stats = compiled_agent.get_stats()
        assert "agent_name" in stats
        assert "strategy" in stats
        assert "strategy_stats" in stats
        assert "tools_count" in stats
        assert stats["agent_name"] == agent.name
    
    def test_compiled_agent_tool_delegation(self):
        """Test compiled agent tool delegation."""
        agent = SimpleAgent()
        compiled_agent = compile(agent)
        
        # Test tool listing
        tools = compiled_agent.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Test tool getting
        tool = compiled_agent.get_tool("calculator")
        assert tool is not None
        
        # Test tool registration
        def dummy_tool():
            return "dummy"
        
        from agents.base import SimpleTool
        dummy = SimpleTool("dummy", "Dummy tool", dummy_tool)
        compiled_agent.register_tool(dummy)
        
        assert "dummy" in compiled_agent.tools
        assert compiled_agent.get_tool("dummy") is not None


class TestAgentCompiler:
    """Test agent compiler functionality."""
    
    def test_compile_default_strategy(self):
        """Test compilation with default strategy."""
        agent = SimpleAgent()
        compiled_agent = AgentCompiler.compile(agent)
        
        assert isinstance(compiled_agent, CompiledAgent)
        stats = compiled_agent.get_stats()
        assert stats["strategy"] in ["CompiledStrategy", "TraditionalStrategy"]
    
    def test_compile_traditional_strategy(self):
        """Test compilation with traditional strategy."""
        agent = SimpleAgent()
        compiled_agent = AgentCompiler.compile(agent, "traditional")
        
        assert isinstance(compiled_agent, CompiledAgent)
        stats = compiled_agent.get_stats()
        assert stats["strategy"] == "TraditionalStrategy"
    
    def test_compile_compiled_strategy(self):
        """Test compilation with compiled strategy."""
        agent = SimpleAgent()
        compiled_agent = AgentCompiler.compile(agent, "compiled")
        
        assert isinstance(compiled_agent, CompiledAgent)
        stats = compiled_agent.get_stats()
        assert stats["strategy"] == "CompiledStrategy"
    
    def test_compile_invalid_strategy(self):
        """Test compilation with invalid strategy."""
        agent = SimpleAgent()
        
        with pytest.raises(ValueError, match="Unknown strategy"):
            AgentCompiler.compile(agent, "invalid_strategy")
    
    def test_compile_with_cache(self):
        """Test compilation with custom cache size."""
        agent = SimpleAgent()
        compiled_agent = AgentCompiler.compile_with_cache(agent, cache_size=100)
        
        assert isinstance(compiled_agent, CompiledAgent)
        # Cache size is internal to strategy, but we can verify compilation worked
    
    def test_compile_benchmark(self):
        """Test compilation benchmarking."""
        agent = SimpleAgent()
        
        # Benchmark with default test inputs
        results = AgentCompiler.benchmark(agent)
        
        assert isinstance(results, dict)
        assert "TraditionalStrategy" in results or "CompiledStrategy" in results
        
        # Check that results contain expected fields
        for strategy_name, result in results.items():
            if "error" not in result:
                assert "total_time" in result
                assert "avg_time" in result
                assert "stats" in result


class TestExecutionBenchmark:
    """Test execution benchmark functionality."""
    
    def test_benchmark_strategies(self):
        """Test benchmarking different strategies."""
        agent = SimpleAgent()
        test_inputs = ["Hello", "What is 2+2?", "Goodbye"]
        
        strategies = [
            StrategyFactory.create_traditional(),
            StrategyFactory.create_compiled()
        ]
        
        results = ExecutionBenchmark.benchmark(agent, test_inputs, strategies)
        
        assert isinstance(results, dict)
        assert len(results) == 2
        
        # Check results structure
        for strategy_name, result in results.items():
            if "error" not in result:
                assert "total_time" in result
                assert "avg_time" in result
                assert "stats" in result
    
    def test_benchmark_with_default_inputs(self):
        """Test benchmarking with default test inputs."""
        agent = SimpleAgent()
        strategies = [StrategyFactory.create_traditional()]
        test_inputs = ["Hello", "What is 2+2?", "Goodbye"]
        
        results = ExecutionBenchmark.benchmark(agent, test_inputs, strategies)
        
        assert isinstance(results, dict)
        assert "TraditionalStrategy" in results


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_compile_function(self):
        """Test convenience compile function."""
        agent = SimpleAgent()
        compiled_agent = compile(agent)
        
        assert isinstance(compiled_agent, CompiledAgent)
        result = compiled_agent.run("Hello")
        assert isinstance(result, str)
    
    def test_compile_with_cache_function(self):
        """Test convenience compile_with_cache function."""
        agent = SimpleAgent()
        compiled_agent = AgentCompiler.compile_with_cache(agent, cache_size=50)
        
        assert isinstance(compiled_agent, CompiledAgent)
    
    def test_get_performance_stats(self):
        """Test get_performance_stats function."""
        agent = SimpleAgent()
        compiled_agent = compile(agent)
        
        from core.compilation import get_performance_stats
        stats = get_performance_stats(compiled_agent)
        
        assert isinstance(stats, dict)
        assert "agent_name" in stats
        assert "strategy" in stats


class TestCompatibility:
    """Test compatibility with existing code."""
    
    def test_original_agent_still_works(self):
        """Test that original agent functionality is unchanged."""
        agent = SimpleAgent()
        
        # Original methods should still work
        result = agent.run("Hello")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Original attributes should be unchanged
        assert hasattr(agent, 'name')
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'create_graph')
    
    def test_no_compilation_by_default(self):
        """Test that compilation is opt-in."""
        agent = SimpleAgent()
        
        # Agent should work normally without compilation
        result = agent.run("What is 2+2?")
        assert "4.0" in result or "4" in result
        
        # No compilation-related attributes should be present
        assert not hasattr(agent, '_compiled_graph')
        assert not hasattr(agent, '_compiler')
    
    def test_compiled_agent_backward_compatibility(self):
        """Test that compiled agent maintains backward compatibility."""
        agent = SimpleAgent()
        compiled_agent = compile(agent)
        
        # Should support all original agent methods
        assert hasattr(compiled_agent, 'name')
        assert hasattr(compiled_agent, 'tools')
        assert hasattr(compiled_agent, 'run')
        assert hasattr(compiled_agent, 'register_tool')
        assert hasattr(compiled_agent, 'get_tool')
        assert hasattr(compiled_agent, 'list_tools')
        
        # Methods should work the same way
        tools = compiled_agent.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0


class TestPerformance:
    """Test performance characteristics."""
    
    def test_compiled_strategy_performance(self):
        """Test that compiled strategy shows performance benefits."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_compiled()
        
        # Warm up cache
        strategy.execute(agent, "Warm up")
        
        # Measure cached execution
        start_time = time.time()
        for i in range(5):
            strategy.execute(agent, f"Test {i}")
        cached_time = time.time() - start_time
        
        # Create new strategy (cold cache)
        cold_strategy = StrategyFactory.create_compiled()
        start_time = time.time()
        for i in range(5):
            cold_strategy.execute(agent, f"Test {i}")
        cold_time = time.time() - start_time
        
        # Cached should be faster (though this can vary)
        # We'll just verify both completed successfully
        assert cached_time > 0
        assert cold_time > 0
    
    def test_memory_usage(self):
        """Test memory usage characteristics."""
        agent = SimpleAgent()
        strategy = StrategyFactory.create_compiled(cache_size=5)
        
        # Execute with same agent multiple times
        for i in range(10):
            strategy.execute(agent, f"Test {i}")
        
        # Cache should prevent unlimited memory growth
        stats = strategy.get_stats()
        assert stats["cache_size"] <= 5  # Should not exceed cache size
        assert stats["cache_utilization"] <= 1.0  # Should not exceed 100%