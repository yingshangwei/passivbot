"""
策略基类定义

所有自定义策略都应该继承自BaseStrategy类，并实现其抽象方法。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            config: 策略配置字典
        """
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"strategy.{self.name}")
        
        # 从配置中获取策略参数
        self.strategy_params = config.get('strategy', {})
        
        self.logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    def calc_entries(self, pside: str, symbol: str, **kwargs) -> List[Dict]:
        """
        计算入场订单
        
        Args:
            pside: 仓位方向 ('long' 或 'short')
            symbol: 交易对符号
            **kwargs: 策略执行所需的参数
            
        Returns:
            List[Dict]: 入场订单列表，每个订单包含以下字段：
                - qty: 订单数量
                - price: 订单价格
                - order_type: 订单类型
                - strategy: 策略名称
        """
        pass
    
    @abstractmethod
    def calc_closes(self, pside: str, symbol: str, **kwargs) -> List[Dict]:
        """
        计算平仓订单
        
        Args:
            pside: 仓位方向 ('long' 或 'short')
            symbol: 交易对符号
            **kwargs: 策略执行所需的参数
            
        Returns:
            List[Dict]: 平仓订单列表，每个订单包含以下字段：
                - qty: 订单数量
                - price: 订单价格
                - order_type: 订单类型
                - strategy: 策略名称
        """
        pass
    
    def get_strategy_params(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        Returns:
            Dict[str, Any]: 策略参数字典
        """
        return self.strategy_params
    
    def get_config_value(self, key_path: List[str], default: Any = None) -> Any:
        """
        从配置中获取值
        
        Args:
            key_path: 配置键路径，如 ['bot', 'long', 'entry_grid_spacing_pct']
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        value = self.config
        for key in key_path:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def validate_order(self, order: Dict) -> bool:
        """
        验证订单格式
        
        Args:
            order: 订单字典
            
        Returns:
            bool: 订单是否有效
        """
        required_fields = ['qty', 'price', 'order_type']
        return all(field in order for field in required_fields)
    
    def log_strategy_action(self, action: str, pside: str, symbol: str, **kwargs):
        """
        记录策略行为日志
        
        Args:
            action: 行为描述
            pside: 仓位方向
            symbol: 交易对
            **kwargs: 额外信息
        """
        self.logger.info(f"{action} - {pside} {symbol}: {kwargs}")
    
    def on_market_data_update(self, symbol: str, market_data: Dict[str, Any]):
        """
        市场数据更新回调（可选实现）
        
        Args:
            symbol: 交易对符号
            market_data: 市场数据
        """
        pass
    
    def on_position_update(self, symbol: str, pside: str, position: Dict[str, Any]):
        """
        仓位更新回调（可选实现）
        
        Args:
            symbol: 交易对符号
            pside: 仓位方向
            position: 仓位信息
        """
        pass
    
    def on_order_filled(self, symbol: str, order: Dict[str, Any]):
        """
        订单成交回调（可选实现）
        
        Args:
            symbol: 交易对符号
            order: 成交订单信息
        """
        pass
