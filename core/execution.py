"""Execution strategies for agents - Open/Closed Principle compliant."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.state import AgentState
from core.graph import Graph
import logging
import hashlib
import time


logger = logging.getLogger(__name__)


class ExecutionStrategy(ABC):
    """Abstract base class for agent execution strategies."""
    
    @abstractmethod
    def execute(self, agent, user_input: str) -> str:
        """Execute agent with given input using this strategy."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this strategy."""
        pass


class TraditionalStrategy(ExecutionStrategy):
    """Traditional execution strategy - creates graph on each execution."""
    
    def __init__(self):
        self.execution_count = 0
        self.total_time = 0.0
    
    def execute(self, agent, user_input: str) -> str:
        """Execute agent using traditional approach."""
        start_time = time.time()
        
        # Use existing agent methods unchanged
        initial_state = agent.process_input(user_input)
        graph = agent.create_graph()
        
        # Validate and execute
        issues = graph.validate()
        if issues:
            logger.warning(f"Graph validation issues: {issues}")
        
        final_state = graph.execute(initial_state)
        result = agent.format_output(final_state)
        
        # Update statistics
        self.execution_count += 1
        self.total_time += time.time() - start_time
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_time = self.total_time / self.execution_count if self.execution_count > 0 else 0
        return {
            "strategy": "traditional",
            "execution_count": self.execution_count,
            "total_time": self.total_time,
            "avg_time": avg_time
        }


class GraphCache:
    """Simple cache for compiled graphs."""
    
    def __init__(self, max_size: int = 50):
        self._cache: Dict[str, Graph] = {}
        self._validation_cache: Dict[str, bool] = {}
        self._max_size = max_size
    
    def _generate_key(self, agent) -> str:
        """Generate cache key for agent."""
        # Key based on agent identity and tools
        tools_key = tuple(sorted(agent.tools.keys()))
        key_data = f"{agent.__class__.__name__}_{agent.name}_{tools_key}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, agent) -> Optional[Graph]:
        """Get cached graph for agent."""
        key = self._generate_key(agent)
        return self._cache.get(key)
    
    def set(self, agent, graph: Graph) -> str:
        """Cache graph for agent."""
        key = self._generate_key(agent)
        
        # Simple eviction policy
        if len(self._cache) >= self._max_size:
            self._cache.clear()
            self._validation_cache.clear()
        
        self._cache[key] = graph
        return key
    
    def is_valid(self, key: str) -> bool:
        """Check if cached graph is valid."""
        if key not in self._validation_cache:
            graph = self._cache[key]
            issues = graph.validate()
            self._validation_cache[key] = len(issues) == 0
        return self._validation_cache[key]
    
    def clear(self):
        """Clear all cached graphs."""
        self._cache.clear()
        self._validation_cache.clear()


class CompiledStrategy(ExecutionStrategy):
    """Compiled execution strategy - caches and reuses graphs."""
    
    def __init__(self, cache_size: int = 50):
        self.cache = GraphCache(cache_size)
        self.execution_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_time = 0.0
        self.compilation_time = 0.0
    
    def execute(self, agent, user_input: str) -> str:
        """Execute agent using compiled approach."""
        start_time = time.time()
        
        # Try to get cached graph
        graph = self.cache.get(agent)
        
        if graph is None:
            # Cache miss - create and cache graph
            compilation_start = time.time()
            graph = agent.create_graph()
            cache_key = self.cache.set(agent, graph)
            self.compilation_time += time.time() - compilation_start
            self.cache_misses += 1
            logger.debug(f"Graph cache miss for {agent.name}, compiled and cached")
        else:
            # Cache hit
            self.cache_hits += 1
            logger.debug(f"Graph cache hit for {agent.name}")
        
        # Validate cached graph
        cache_key = self.cache._generate_key(agent)
        if not self.cache.is_valid(cache_key):
            logger.warning(f"Cached graph validation failed for {agent.name}")
            # Fallback to fresh graph
            graph = agent.create_graph()
        
        # Execute using existing agent methods
        initial_state = agent.process_input(user_input)
        final_state = graph.execute(initial_state)
        result = agent.format_output(final_state)
        
        # Update statistics
        self.execution_count += 1
        self.total_time += time.time() - start_time
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        avg_time = self.total_time / self.execution_count if self.execution_count > 0 else 0
        
        return {
            "strategy": "compiled",
            "execution_count": self.execution_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_time": self.total_time,
            "avg_time": avg_time,
            "compilation_time": self.compilation_time,
            "cache_size": len(self.cache._cache),
            "cache_utilization": len(self.cache._cache) / self.cache._max_size
        }
    
    def clear_cache(self):
        """Clear the graph cache."""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.compilation_time = 0.0
        logger.info("Compiled strategy cache cleared")


class StrategyFactory:
    """Factory for creating execution strategies."""
    
    @staticmethod
    def create_traditional() -> TraditionalStrategy:
        """Create traditional execution strategy."""
        return TraditionalStrategy()
    
    @staticmethod
    def create_compiled(cache_size: int = 50) -> CompiledStrategy:
        """Create compiled execution strategy."""
        return CompiledStrategy(cache_size)
    
    @staticmethod
    def create_best_automatic() -> ExecutionStrategy:
        """Create the best strategy based on heuristics."""
        # For now, default to compiled as it's generally better
        return CompiledStrategy()


class ExecutionBenchmark:
    """Utility for benchmarking different execution strategies."""
    
    @staticmethod
    def benchmark(agent, test_inputs: list, strategies: list) -> Dict[str, Any]:
        """Benchmark multiple execution strategies."""
        results = {}
        
        for strategy in strategies:
            strategy_name = strategy.__class__.__name__
            start_time = time.time()
            
            try:
                for test_input in test_inputs:
                    strategy.execute(agent, test_input)
                
                total_time = time.time() - start_time
                stats = strategy.get_stats()
                
                results[strategy_name] = {
                    "total_time": total_time,
                    "avg_time": total_time / len(test_inputs),
                    "stats": stats
                }
                
                logger.info(f"{strategy_name} benchmark completed in {total_time:.3f}s")
                
            except Exception as e:
                logger.error(f"{strategy_name} benchmark failed: {e}")
                results[strategy_name] = {"error": str(e)}
        
        return results