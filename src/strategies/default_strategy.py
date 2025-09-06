"""
默认策略实现

这是Passivbot的默认策略，使用Rust组件实现网格+追踪策略。
"""

from typing import List, Dict, Any
import passivbot_rust as pbr
from .base_strategy import BaseStrategy

class DefaultStrategy(BaseStrategy):
    """默认网格+追踪策略"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger.info("Initialized default grid + trailing strategy")
    
    def calc_entries(self, pside: str, symbol: str, **kwargs) -> List[Dict]:
        """
        使用Rust组件计算入场订单
        
        Args:
            pside: 仓位方向 ('long' 或 'short')
            symbol: 交易对符号
            **kwargs: 策略执行参数
            
        Returns:
            List[Dict]: 入场订单列表
        """
        try:
            # 调用Rust组件计算入场订单
            entries = getattr(pbr, f"calc_entries_{pside}_py")(
                kwargs['qty_steps'],
                kwargs['price_steps'],
                kwargs['min_qtys'],
                kwargs['min_costs'],
                kwargs['c_mults'],
                self.get_config_value(["bot", pside, "entry_grid_double_down_factor"]),
                self.get_config_value(["bot", pside, "entry_grid_spacing_weight"]),
                self.get_config_value(["bot", pside, "entry_grid_spacing_pct"]),
                self.get_config_value(["bot", pside, "entry_initial_ema_dist"]),
                self.get_config_value(["bot", pside, "entry_initial_qty_pct"]),
                self.get_config_value(["bot", pside, "entry_trailing_double_down_factor"]),
                self.get_config_value(["bot", pside, "entry_trailing_grid_ratio"]),
                self.get_config_value(["bot", pside, "entry_trailing_retracement_pct"]),
                self.get_config_value(["bot", pside, "entry_trailing_threshold_pct"]),
                self.get_config_value(["bot", pside, "wallet_exposure_limit"]),
                kwargs['balance'],
                kwargs['position_size'],
                kwargs['position_price'],
                kwargs.get('trailing_min_since_open', 0.0),
                kwargs.get('trailing_max_since_min', 0.0),
                kwargs.get('trailing_max_since_open', 0.0),
                kwargs.get('trailing_min_since_max', 0.0),
                kwargs.get('ema_min', 0.0),
                kwargs.get('current_price', 0.0),
            )
            
            # 转换为标准格式
            formatted_entries = []
            for entry in entries:
                if hasattr(entry, 'qty') and hasattr(entry, 'price') and hasattr(entry, 'order_type'):
                    formatted_entries.append({
                        'qty': entry.qty,
                        'price': entry.price,
                        'order_type': entry.order_type,
                        'strategy': 'default'
                    })
            
            self.log_strategy_action("calc_entries", pside, symbol, 
                                   count=len(formatted_entries))
            
            return formatted_entries
            
        except Exception as e:
            self.logger.error(f"Error calculating entries for {pside} {symbol}: {e}")
            return []
    
    def calc_closes(self, pside: str, symbol: str, **kwargs) -> List[Dict]:
        """
        使用Rust组件计算平仓订单
        
        Args:
            pside: 仓位方向 ('long' 或 'short')
            symbol: 交易对符号
            **kwargs: 策略执行参数
            
        Returns:
            List[Dict]: 平仓订单列表
        """
        try:
            # 调用Rust组件计算平仓订单
            closes = getattr(pbr, f"calc_closes_{pside}_py")(
                kwargs['qty_steps'],
                kwargs['price_steps'],
                kwargs['min_qtys'],
                kwargs['min_costs'],
                kwargs['c_mults'],
                self.get_config_value(["bot", pside, "close_grid_markup_end"]),
                self.get_config_value(["bot", pside, "close_grid_markup_start"]),
                self.get_config_value(["bot", pside, "close_grid_qty_pct"]),
                self.get_config_value(["bot", pside, "close_trailing_grid_ratio"]),
                self.get_config_value(["bot", pside, "close_trailing_qty_pct"]),
                self.get_config_value(["bot", pside, "close_trailing_retracement_pct"]),
                self.get_config_value(["bot", pside, "close_trailing_threshold_pct"]),
                kwargs['position_size'],
                kwargs['position_price'],
                kwargs.get('trailing_min_since_open', 0.0),
                kwargs.get('trailing_max_since_min', 0.0),
                kwargs.get('trailing_max_since_open', 0.0),
                kwargs.get('trailing_min_since_max', 0.0),
                kwargs.get('ema_min', 0.0),
                kwargs.get('current_price', 0.0),
            )
            
            # 转换为标准格式
            formatted_closes = []
            for close in closes:
                if hasattr(close, 'qty') and hasattr(close, 'price') and hasattr(close, 'order_type'):
                    formatted_closes.append({
                        'qty': close.qty,
                        'price': close.price,
                        'order_type': close.order_type,
                        'strategy': 'default'
                    })
            
            self.log_strategy_action("calc_closes", pside, symbol, 
                                   count=len(formatted_closes))
            
            return formatted_closes
            
        except Exception as e:
            self.logger.error(f"Error calculating closes for {pside} {symbol}: {e}")
            return []
