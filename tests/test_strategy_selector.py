"""Tests for strategy selection functionality."""

import pytest
import os
from unittest.mock import patch
from core.strategy_selector import StrategySelector, strategy_selector
from core.execution import TraditionalStrategy, CompiledStrategy, StrategyFactory
from agents.simple import SimpleAgent


class TestStrategySelector:
    """Test strategy selector functionality."""
    
    def test_strategy_selector_initialization(self):
        """Test strategy selector initialization."""
        selector = StrategySelector()
        assert selector.default_strategy == "traditional"  # Default value
        assert selector.enable_auto_switch is False  # Default value
    
    def test_select_strategy_request_level(self):
        """Test strategy selection at request level."""
        selector = StrategySelector()
        
        # Request level should take precedence
        strategy = selector.select_strategy(request_strategy="compiled")
        assert strategy == "compiled"
        
        strategy = selector.select_strategy(request_strategy="traditional")
        assert strategy == "traditional"
    
    def test_select_strategy_header_level(self):
        """Test strategy selection at header level."""
        selector = StrategySelector()
        
        # Header level should work when no request strategy
        strategy = selector.select_strategy(header_strategy="compiled")
        assert strategy == "compiled"
        
        # Request level should override header level
        strategy = selector.select_strategy(
            request_strategy="traditional",
            header_strategy="compiled"
        )
        assert strategy == "traditional"
    
    def test_select_strategy_environment_level(self):
        """Test strategy selection at environment level."""
        selector = StrategySelector()
        
        # Should fall back to environment default
        strategy = selector.select_strategy()
        assert strategy == "traditional"
        
        # Test with custom environment
        with patch.dict(os.environ, {'DEFAULT_STRATEGY': 'compiled'}):
            selector_env = StrategySelector()
            strategy = selector_env.select_strategy()
            assert strategy == "compiled"
    
    def test_select_strategy_auto_switching(self):
        """Test automatic strategy switching based on complexity."""
        with patch.dict(os.environ, {'AUTO_STRATEGY': 'true'}):
            selector = StrategySelector()
            assert selector.enable_auto_switch is True
            
            # High complexity should use compiled
            strategy = selector.select_strategy(request_complexity=8)
            assert strategy == "compiled"
            
            # Low complexity should use traditional
            strategy = selector.select_strategy(request_complexity=2)
            assert strategy == "traditional"
            
            # Medium complexity should use compiled
            strategy = selector.select_strategy(request_complexity=5)
            assert strategy == "compiled"
    
    def test_create_strategy_instance(self):
        """Test creating strategy instances."""
        selector = StrategySelector()
        
        # Test creating traditional strategy
        strategy = selector.create_strategy(request_strategy="traditional")
        assert isinstance(strategy, TraditionalStrategy)
        
        # Test creating compiled strategy
        strategy = selector.create_strategy(request_strategy="compiled")
        assert isinstance(strategy, CompiledStrategy)
        
        # Test default strategy
        strategy = selector.create_strategy()
        assert isinstance(strategy, TraditionalStrategy)
    
    def test_invalid_strategy_handling(self):
        """Test handling of invalid strategy names."""
        selector = StrategySelector()
        
        # Invalid request strategy should fall back
        strategy = selector.select_strategy(request_strategy="invalid")
        assert strategy == "traditional"
        
        # Invalid header strategy should fall back
        strategy = selector.select_strategy(header_strategy="invalid")
        assert strategy == "traditional"


class TestGlobalStrategySelector:
    """Test global strategy selector instance."""
    
    def test_global_selector_exists(self):
        """Test that global selector instance exists."""
        assert strategy_selector is not None
        assert isinstance(strategy_selector, StrategySelector)
    
    def test_global_selector_default_behavior(self):
        """Test global selector default behavior."""
        strategy = strategy_selector.create_strategy()
        assert isinstance(strategy, TraditionalStrategy)
    
    def test_global_selector_with_parameters(self):
        """Test global selector with custom parameters."""
        strategy = strategy_selector.create_strategy(
            request_strategy="compiled",
            header_strategy="traditional",
            request_complexity=5
        )
        assert isinstance(strategy, CompiledStrategy)


class TestStrategySelectorIntegration:
    """Test strategy selector integration with execution."""
    
    def test_strategy_execution_with_selector(self):
        """Test that strategies selected by selector work correctly."""
        selector = StrategySelector()
        agent = SimpleAgent()
        
        # Test traditional strategy
        strategy = selector.create_strategy(request_strategy="traditional")
        result = strategy.execute(agent, "Hello")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test compiled strategy
        strategy = selector.create_strategy(request_strategy="compiled")
        result = strategy.execute(agent, "Hello")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_strategy_stats_with_selector(self):
        """Test that strategy stats work with selector."""
        selector = StrategySelector()
        agent = SimpleAgent()
        
        # Test compiled strategy stats
        strategy = selector.create_strategy(request_strategy="compiled")
        strategy.execute(agent, "Test message")
        
        stats = strategy.get_stats()
        assert "strategy" in stats
        assert "execution_count" in stats
        assert stats["strategy"] == "compiled"
        assert stats["execution_count"] == 1