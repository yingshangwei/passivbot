"""
策略管理器

负责策略的注册、加载和管理。
"""

from typing import Dict, Type, Optional, Any
import logging
from .base_strategy import BaseStrategy

class StrategyManager:
    """策略管理器"""
    
    def __init__(self):
        self.strategies: Dict[str, Type[BaseStrategy]] = {}
        self.active_strategy: Optional[BaseStrategy] = None
        self.logger = logging.getLogger("strategy.manager")
        
        # 注册默认策略
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认策略"""
        try:
            from .default_strategy import DefaultStrategy
            self.register_strategy('default', DefaultStrategy)
            self.logger.info("Registered default strategy")
        except ImportError as e:
            self.logger.warning(f"Failed to register default strategy: {e}")
    
    def register_strategy(self, name: str, strategy_class: Type[BaseStrategy]):
        """
        注册新策略
        
        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"Strategy class must inherit from BaseStrategy")
        
        self.strategies[name] = strategy_class
        self.logger.info(f"Registered strategy: {name}")
    
    def unregister_strategy(self, name: str):
        """
        注销策略
        
        Args:
            name: 策略名称
        """
        if name in self.strategies:
            del self.strategies[name]
            self.logger.info(f"Unregistered strategy: {name}")
    
    def list_strategies(self) -> list:
        """
        列出所有已注册的策略
        
        Returns:
            list: 策略名称列表
        """
        return list(self.strategies.keys())
    
    def load_strategy(self, name: str, config: Dict[str, Any]) -> BaseStrategy:
        """
        加载策略
        
        Args:
            name: 策略名称
            config: 策略配置
            
        Returns:
            BaseStrategy: 策略实例
        """
        if name not in self.strategies:
            available = ', '.join(self.strategies.keys())
            raise ValueError(f"Strategy '{name}' not found. Available strategies: {available}")
        
        try:
            strategy_class = self.strategies[name]
            self.active_strategy = strategy_class(config)
            self.logger.info(f"Loaded strategy: {name}")
            return self.active_strategy
        except Exception as e:
            self.logger.error(f"Failed to load strategy '{name}': {e}")
            raise
    
    def get_active_strategy(self) -> Optional[BaseStrategy]:
        """
        获取当前活跃策略
        
        Returns:
            Optional[BaseStrategy]: 当前活跃策略实例
        """
        return self.active_strategy
    
    def reload_strategy(self, name: str, config: Dict[str, Any]) -> BaseStrategy:
        """
        重新加载策略
        
        Args:
            name: 策略名称
            config: 策略配置
            
        Returns:
            BaseStrategy: 新的策略实例
        """
        self.logger.info(f"Reloading strategy: {name}")
        return self.load_strategy(name, config)
    
    def get_strategy_info(self, name: str) -> Dict[str, Any]:
        """
        获取策略信息
        
        Args:
            name: 策略名称
            
        Returns:
            Dict[str, Any]: 策略信息
        """
        if name not in self.strategies:
            raise ValueError(f"Strategy '{name}' not found")
        
        strategy_class = self.strategies[name]
        return {
            'name': name,
            'class': strategy_class.__name__,
            'module': strategy_class.__module__,
            'doc': strategy_class.__doc__,
        }
