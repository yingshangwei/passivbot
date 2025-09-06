"""
Passivbot 策略插件系统

这个模块提供了自定义策略的开发框架，允许用户实现自己的交易策略
而无需修改Passivbot的核心代码。
"""

from .base_strategy import BaseStrategy
from .strategy_manager import StrategyManager
from .default_strategy import DefaultStrategy

__all__ = [
    'BaseStrategy',
    'StrategyManager', 
    'DefaultStrategy',
]
