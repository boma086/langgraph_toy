"""Configuration-driven strategy selection."""

import os
from typing import Optional
from core.execution import StrategyFactory, ExecutionStrategy


class StrategySelector:
    """Multi-level strategy selection with fallback."""
    
    def __init__(self):
        self.default_strategy = os.getenv("DEFAULT_STRATEGY", "traditional")
        self.enable_auto_switch = os.getenv("AUTO_STRATEGY", "false").lower() == "true"
    
    def select_strategy(self, 
                       request_strategy: Optional[str] = None,
                       header_strategy: Optional[str] = None,
                       request_complexity: Optional[int] = None) -> str:
        """Select execution strategy with multi-level fallback."""
        
        # Level 1: Request-level explicit specification
        if request_strategy and request_strategy in ["traditional", "compiled", "auto"]:
            return request_strategy
        
        # Level 2: Header-level specification
        if header_strategy and header_strategy in ["traditional", "compiled", "auto"]:
            return header_strategy
        
        # Level 3: Auto-selection based on complexity
        if self.enable_auto_switch and request_complexity:
            if request_complexity > 7:  # High complexity
                return "compiled"
            elif request_complexity < 3:  # Low complexity  
                return "traditional"
            else:  # Medium complexity
                return "compiled"  # Default to compiled for medium
        
        # Level 4: Environment configuration
        return self.default_strategy
    
    def create_strategy(self, **kwargs) -> 'ExecutionStrategy':
        """Create strategy instance based on selection."""
        strategy_type = self.select_strategy(**kwargs)
        if strategy_type == "auto":
            return StrategyFactory.create_best_automatic()
        elif strategy_type == "traditional":
            return StrategyFactory.create_traditional()
        elif strategy_type == "compiled":
            return StrategyFactory.create_compiled()
        else:
            # Default to traditional for invalid strategy types
            return StrategyFactory.create_traditional()


# Global selector instance
strategy_selector = StrategySelector()