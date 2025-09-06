#!/usr/bin/env python3
"""
策略测试脚本

用于测试自定义策略的功能和性能。
"""

import sys
import os
import json
import logging
from typing import Dict, Any

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from strategies.strategy_manager import StrategyManager
from strategies.ma_crossover_strategy import MACrossoverStrategy

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_strategy_manager():
    """测试策略管理器"""
    print("=== 测试策略管理器 ===")
    
    manager = StrategyManager()
    
    # 列出所有策略
    strategies = manager.list_strategies()
    print(f"可用策略: {strategies}")
    
    # 注册MA交叉策略
    manager.register_strategy('ma_crossover', MACrossoverStrategy)
    print("已注册MA交叉策略")
    
    # 再次列出策略
    strategies = manager.list_strategies()
    print(f"注册后可用策略: {strategies}")
    
    return manager

def test_ma_crossover_strategy():
    """测试MA交叉策略"""
    print("\n=== 测试MA交叉策略 ===")
    
    # 创建测试配置
    config = {
        'strategy': {
            'name': 'ma_crossover',
            'params': {
                'fast_period': 5,
                'slow_period': 10,
                'position_size': 0.1,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.04
            }
        }
    }
    
    # 创建策略实例
    strategy = MACrossoverStrategy(config)
    print(f"策略名称: {strategy.name}")
    print(f"策略参数: {strategy.get_strategy_params()}")
    
    # 模拟价格数据
    symbol = "BTCUSDT"
    prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]
    
    # 测试入场逻辑
    print("\n--- 测试入场逻辑 ---")
    for i, price in enumerate(prices):
        kwargs = {
            'current_price': price,
            'balance': 10000,
            'position_size': 0,
            'position_price': 0
        }
        
        # 更新价格历史
        strategy._update_price_history(symbol, price)
        
        # 计算入场订单
        entries = strategy.calc_entries('long', symbol, **kwargs)
        if entries:
            print(f"价格 {price}: 生成入场订单 {entries}")
        
        # 如果有仓位，测试平仓逻辑
        if i > 10:  # 模拟有仓位的情况
            kwargs['position_size'] = 0.1
            kwargs['position_price'] = 110
            
            closes = strategy.calc_closes('long', symbol, **kwargs)
            if closes:
                print(f"价格 {price}: 生成平仓订单 {closes}")
    
    # 获取策略状态
    status = strategy.get_strategy_status(symbol)
    print(f"\n策略状态: {status}")

def test_strategy_with_manager():
    """使用策略管理器测试策略"""
    print("\n=== 使用策略管理器测试 ===")
    
    manager = StrategyManager()
    
    # 加载MA交叉策略
    config = {
        'strategy': {
            'name': 'ma_crossover',
            'params': {
                'fast_period': 5,
                'slow_period': 10,
                'position_size': 0.1
            }
        }
    }
    
    try:
        strategy = manager.load_strategy('ma_crossover', config)
        print(f"成功加载策略: {strategy.name}")
        
        # 获取策略信息
        info = manager.get_strategy_info('ma_crossover')
        print(f"策略信息: {info}")
        
    except Exception as e:
        print(f"加载策略失败: {e}")

def test_config_loading():
    """测试配置文件加载"""
    print("\n=== 测试配置文件加载 ===")
    
    config_file = "my_ma_crossover_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"配置文件加载成功")
        print(f"策略名称: {config['strategy']['name']}")
        print(f"策略参数: {config['strategy']['params']}")
        
        # 使用配置创建策略
        manager = StrategyManager()
        manager.register_strategy('ma_crossover', MACrossoverStrategy)
        
        strategy = manager.load_strategy('ma_crossover', config)
        print(f"使用配置文件创建策略成功: {strategy.name}")
        
    else:
        print(f"配置文件 {config_file} 不存在")

def main():
    """主函数"""
    setup_logging()
    
    print("Passivbot 自定义策略测试")
    print("=" * 50)
    
    try:
        # 测试策略管理器
        manager = test_strategy_manager()
        
        # 测试MA交叉策略
        test_ma_crossover_strategy()
        
        # 使用策略管理器测试
        test_strategy_with_manager()
        
        # 测试配置文件加载
        test_config_loading()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
