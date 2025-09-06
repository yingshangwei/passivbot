"""
移动平均线交叉策略示例

这是一个简单的自定义策略示例，展示如何实现基于技术指标的策略。
"""

import numpy as np
from typing import List, Dict, Any
from .base_strategy import BaseStrategy

class MACrossoverStrategy(BaseStrategy):
    """移动平均线交叉策略"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 从配置中获取策略参数
        strategy_params = self.get_strategy_params()
        self.fast_period = strategy_params.get('fast_period', 10)
        self.slow_period = strategy_params.get('slow_period', 20)
        self.position_size = strategy_params.get('position_size', 0.1)
        self.stop_loss_pct = strategy_params.get('stop_loss_pct', 0.02)
        self.take_profit_pct = strategy_params.get('take_profit_pct', 0.04)
        
        # 价格历史缓存
        self.price_history = {}
        
        self.logger.info(f"MA Crossover Strategy initialized: "
                        f"fast={self.fast_period}, slow={self.slow_period}, "
                        f"size={self.position_size}")
    
    def _update_price_history(self, symbol: str, price: float):
        """更新价格历史"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        
        # 保持历史长度不超过慢线周期的2倍
        max_length = self.slow_period * 2
        if len(self.price_history[symbol]) > max_length:
            self.price_history[symbol] = self.price_history[symbol][-max_length:]
    
    def _calculate_ma(self, prices: List[float], period: int) -> float:
        """计算移动平均线"""
        if len(prices) < period:
            return 0.0
        return np.mean(prices[-period:])
    
    def _detect_crossover(self, prices: List[float]) -> str:
        """
        检测MA交叉信号
        
        Returns:
            str: 'golden' (金叉), 'death' (死叉), 'none' (无信号)
        """
        if len(prices) < self.slow_period + 1:
            return 'none'
        
        # 计算当前和之前的MA
        current_fast_ma = self._calculate_ma(prices, self.fast_period)
        current_slow_ma = self._calculate_ma(prices, self.slow_period)
        
        prev_prices = prices[:-1]
        prev_fast_ma = self._calculate_ma(prev_prices, self.fast_period)
        prev_slow_ma = self._calculate_ma(prev_prices, self.slow_period)
        
        # 检测交叉
        if prev_fast_ma <= prev_slow_ma and current_fast_ma > current_slow_ma:
            return 'golden'  # 金叉
        elif prev_fast_ma >= prev_slow_ma and current_fast_ma < current_slow_ma:
            return 'death'   # 死叉
        
        return 'none'
    
    def calc_entries(self, pside: str, symbol: str, **kwargs) -> List[Dict]:
        """
        基于MA交叉的入场逻辑
        
        Args:
            pside: 仓位方向 ('long' 或 'short')
            symbol: 交易对符号
            **kwargs: 策略执行参数
            
        Returns:
            List[Dict]: 入场订单列表
        """
        orders = []
        current_price = kwargs.get('current_price', 0)
        balance = kwargs.get('balance', 0)
        
        if current_price <= 0 or balance <= 0:
            return orders
        
        # 更新价格历史
        self._update_price_history(symbol, current_price)
        
        # 获取价格历史
        prices = self.price_history.get(symbol, [])
        if len(prices) < self.slow_period:
            return orders
        
        # 检测交叉信号
        signal = self._detect_crossover(prices)
        
        # 计算订单数量
        qty = balance * self.position_size / current_price
        
        # 根据信号和仓位方向生成订单
        if signal == 'golden' and pside == 'long':
            # 金叉买入信号
            orders.append({
                'qty': qty,
                'price': current_price,
                'order_type': 'market_buy',
                'strategy': 'ma_crossover',
                'signal': 'golden_cross'
            })
            self.log_strategy_action("Entry signal", pside, symbol, 
                                   signal='golden_cross', price=current_price)
        
        elif signal == 'death' and pside == 'short':
            # 死叉卖出信号
            orders.append({
                'qty': -qty,
                'price': current_price,
                'order_type': 'market_sell',
                'strategy': 'ma_crossover',
                'signal': 'death_cross'
            })
            self.log_strategy_action("Entry signal", pside, symbol, 
                                   signal='death_cross', price=current_price)
        
        return orders
    
    def calc_closes(self, pside: str, symbol: str, **kwargs) -> List[Dict]:
        """
        基于MA交叉的平仓逻辑
        
        Args:
            pside: 仓位方向 ('long' 或 'short')
            symbol: 交易对符号
            **kwargs: 策略执行参数
            
        Returns:
            List[Dict]: 平仓订单列表
        """
        orders = []
        current_price = kwargs.get('current_price', 0)
        position_size = kwargs.get('position_size', 0)
        position_price = kwargs.get('position_price', 0)
        
        if abs(position_size) < 1e-8 or current_price <= 0:
            return orders
        
        # 更新价格历史
        self._update_price_history(symbol, current_price)
        
        # 获取价格历史
        prices = self.price_history.get(symbol, [])
        if len(prices) < self.slow_period:
            return orders
        
        # 检测交叉信号
        signal = self._detect_crossover(prices)
        
        # 计算止损和止盈价格
        if position_size > 0:  # 多头仓位
            stop_loss_price = position_price * (1 - self.stop_loss_pct)
            take_profit_price = position_price * (1 + self.take_profit_pct)
            
            # 死叉平仓信号
            if signal == 'death':
                orders.append({
                    'qty': -position_size,
                    'price': current_price,
                    'order_type': 'market_sell',
                    'strategy': 'ma_crossover',
                    'signal': 'death_cross_close'
                })
                self.log_strategy_action("Close signal", pside, symbol, 
                                       signal='death_cross_close', price=current_price)
            
            # 止损
            elif current_price <= stop_loss_price:
                orders.append({
                    'qty': -position_size,
                    'price': current_price,
                    'order_type': 'market_sell',
                    'strategy': 'ma_crossover',
                    'signal': 'stop_loss'
                })
                self.log_strategy_action("Stop loss", pside, symbol, 
                                       price=current_price, stop_price=stop_loss_price)
            
            # 止盈
            elif current_price >= take_profit_price:
                orders.append({
                    'qty': -position_size,
                    'price': current_price,
                    'order_type': 'market_sell',
                    'strategy': 'ma_crossover',
                    'signal': 'take_profit'
                })
                self.log_strategy_action("Take profit", pside, symbol, 
                                       price=current_price, target_price=take_profit_price)
        
        elif position_size < 0:  # 空头仓位
            stop_loss_price = position_price * (1 + self.stop_loss_pct)
            take_profit_price = position_price * (1 - self.take_profit_pct)
            
            # 金叉平仓信号
            if signal == 'golden':
                orders.append({
                    'qty': abs(position_size),
                    'price': current_price,
                    'order_type': 'market_buy',
                    'strategy': 'ma_crossover',
                    'signal': 'golden_cross_close'
                })
                self.log_strategy_action("Close signal", pside, symbol, 
                                       signal='golden_cross_close', price=current_price)
            
            # 止损
            elif current_price >= stop_loss_price:
                orders.append({
                    'qty': abs(position_size),
                    'price': current_price,
                    'order_type': 'market_buy',
                    'strategy': 'ma_crossover',
                    'signal': 'stop_loss'
                })
                self.log_strategy_action("Stop loss", pside, symbol, 
                                       price=current_price, stop_price=stop_loss_price)
            
            # 止盈
            elif current_price <= take_profit_price:
                orders.append({
                    'qty': abs(position_size),
                    'price': current_price,
                    'order_type': 'market_buy',
                    'strategy': 'ma_crossover',
                    'signal': 'take_profit'
                })
                self.log_strategy_action("Take profit", pside, symbol, 
                                       price=current_price, target_price=take_profit_price)
        
        return orders
    
    def on_market_data_update(self, symbol: str, market_data: Dict[str, Any]):
        """市场数据更新回调"""
        if 'price' in market_data:
            self._update_price_history(symbol, market_data['price'])
    
    def get_strategy_status(self, symbol: str) -> Dict[str, Any]:
        """获取策略状态"""
        prices = self.price_history.get(symbol, [])
        if len(prices) < self.slow_period:
            return {'status': 'insufficient_data'}
        
        fast_ma = self._calculate_ma(prices, self.fast_period)
        slow_ma = self._calculate_ma(prices, self.slow_period)
        signal = self._detect_crossover(prices)
        
        return {
            'status': 'active',
            'fast_ma': fast_ma,
            'slow_ma': slow_ma,
            'signal': signal,
            'price_count': len(prices)
        }
