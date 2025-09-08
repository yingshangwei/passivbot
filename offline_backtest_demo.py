#!/usr/bin/env python3
"""
离线回测演示

这个脚本演示了Passivbot的核心回测逻辑，完全离线运行。
"""

import sys
import os
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_mock_ohlcv_data(symbol: str, start_date: str, end_date: str, interval: str = '1m'):
    """创建模拟的OHLCV数据"""
    print(f"创建模拟数据: {symbol} from {start_date} to {end_date}")
    
    # 解析日期
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 生成时间序列
    if interval == '1m':
        freq = '1min'
    elif interval == '1h':
        freq = '1H'
    else:
        freq = '1min'
    
    timestamps = pd.date_range(start=start, end=end, freq=freq)
    
    # 生成模拟价格数据（随机游走）
    np.random.seed(42)  # 固定随机种子以便复现
    
    # 初始价格
    initial_price = 50000 if 'BTC' in symbol else 3000
    
    # 生成价格序列（对数正态分布）
    returns = np.random.normal(0, 0.001, len(timestamps))  # 0.1%的标准差
    prices = initial_price * np.exp(np.cumsum(returns))
    
    # 生成OHLCV数据
    data = []
    for i, (ts, price) in enumerate(zip(timestamps, prices)):
        # 生成开盘价、最高价、最低价、收盘价
        open_price = price
        close_price = price * (1 + np.random.normal(0, 0.0005))
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.0002)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.0002)))
        volume = np.random.uniform(100, 1000)
        
        data.append({
            'timestamp': ts,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    print(f"生成了 {len(df)} 条数据")
    print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    return df

def simple_grid_strategy_backtest(ohlcv_data: pd.DataFrame, config: dict):
    """
    简单的网格策略回测
    
    Args:
        ohlcv_data: OHLCV数据
        config: 策略配置
        
    Returns:
        dict: 回测结果
    """
    print("开始简单网格策略回测...")
    
    # 策略参数
    entry_spacing = config['bot']['long']['entry_grid_spacing_pct']
    close_markup = config['bot']['long']['close_grid_markup_start']
    position_size = config['bot']['long']['entry_initial_qty_pct']
    max_positions = int(config['bot']['long']['n_positions'])
    
    # 初始资金
    initial_balance = config['backtest']['starting_balance']
    balance = initial_balance
    
    # 交易记录
    trades = []
    positions = []
    
    # 网格价格点
    current_price = ohlcv_data['close'].iloc[0]
    grid_prices = []
    
    # 生成网格价格点
    for i in range(max_positions):
        grid_price = current_price * (1 - entry_spacing * (i + 1))
        grid_prices.append(grid_price)
    
    print(f"网格价格点: {[f'{p:.2f}' for p in grid_prices]}")
    
    # 模拟交易
    for i, (timestamp, row) in enumerate(ohlcv_data.iterrows()):
        current_price = row['close']
        
        # 检查是否有网格价格被触发
        for j, grid_price in enumerate(grid_prices):
            if current_price <= grid_price and j not in [p['grid_index'] for p in positions]:
                # 触发买入
                qty = balance * position_size / current_price
                balance -= qty * current_price
                
                position = {
                    'grid_index': j,
                    'entry_price': current_price,
                    'qty': qty,
                    'entry_time': timestamp
                }
                positions.append(position)
                
                trades.append({
                    'type': 'buy',
                    'price': current_price,
                    'qty': qty,
                    'timestamp': timestamp,
                    'balance': balance
                })
                
                print(f"买入: 价格 {current_price:.2f}, 数量 {qty:.6f}, 余额 {balance:.2f}")
        
        # 检查平仓条件
        positions_to_close = []
        for pos in positions:
            target_price = pos['entry_price'] * (1 + close_markup)
            if current_price >= target_price:
                # 触发平仓
                balance += pos['qty'] * current_price
                
                trades.append({
                    'type': 'sell',
                    'price': current_price,
                    'qty': pos['qty'],
                    'timestamp': timestamp,
                    'balance': balance,
                    'profit': pos['qty'] * (current_price - pos['entry_price'])
                })
                
                positions_to_close.append(pos)
                print(f"平仓: 价格 {current_price:.2f}, 数量 {pos['qty']:.6f}, 利润 {pos['qty'] * (current_price - pos['entry_price']):.2f}")
        
        # 移除已平仓的仓位
        for pos in positions_to_close:
            positions.remove(pos)
    
    # 计算最终结果
    final_balance = balance
    for pos in positions:
        final_balance += pos['qty'] * current_price
    
    total_return = (final_balance - initial_balance) / initial_balance * 100
    
    # 统计交易
    buy_trades = [t for t in trades if t['type'] == 'buy']
    sell_trades = [t for t in trades if t['type'] == 'sell']
    
    total_profit = sum([t['profit'] for t in sell_trades if 'profit' in t])
    
    result = {
        'initial_balance': initial_balance,
        'final_balance': final_balance,
        'total_return_pct': total_return,
        'total_trades': len(trades),
        'buy_trades': len(buy_trades),
        'sell_trades': len(sell_trades),
        'total_profit': total_profit,
        'remaining_positions': len(positions),
        'trades': trades
    }
    
    return result

def print_backtest_results(result: dict):
    """打印回测结果"""
    print("\n" + "="*50)
    print("回测结果")
    print("="*50)
    print(f"初始资金: ${result['initial_balance']:,.2f}")
    print(f"最终资金: ${result['final_balance']:,.2f}")
    print(f"总收益率: {result['total_return_pct']:.2f}%")
    print(f"总交易次数: {result['total_trades']}")
    print(f"买入次数: {result['buy_trades']}")
    print(f"卖出次数: {result['sell_trades']}")
    print(f"总利润: ${result['total_profit']:,.2f}")
    print(f"剩余仓位: {result['remaining_positions']}")
    
    if result['total_trades'] > 0:
        print(f"\n交易详情:")
        for i, trade in enumerate(result['trades'][:10]):  # 只显示前10笔交易
            print(f"  {i+1}. {trade['type'].upper()}: ${trade['price']:.2f} x {trade['qty']:.6f} @ {trade['timestamp']}")
        
        if len(result['trades']) > 10:
            print(f"  ... 还有 {len(result['trades']) - 10} 笔交易")

def main():
    """主函数"""
    print("Passivbot 离线回测演示")
    print("="*50)
    
    # 创建模拟数据
    symbol = "BTCUSDT"
    start_date = "2024-01-01"
    end_date = "2024-01-07"  # 缩短时间范围以便快速演示
    
    print("1. 创建模拟OHLCV数据...")
    ohlcv_data = create_mock_ohlcv_data(symbol, start_date, end_date)
    
    print("\n2. 加载自定义配置...")
    try:
        import hjson
        with open('my_config_custom.json', 'r') as f:
            config = hjson.load(f)
        print("✅ 成功加载 my_config_custom.json 配置")
        
        # 显示关键配置信息
        coins = config['live']['approved_coins']['long']
        bot_config = config['bot']['long']
        print(f"   币种: {coins}")
        print(f"   杠杆: {config['live']['leverage']}倍")
        print(f"   网格间距: {bot_config['entry_grid_spacing_pct'] * 100}%")
        print(f"   初始入场比例: {bot_config['entry_initial_qty_pct'] * 100}%")
        print(f"   最大持仓: {bot_config['n_positions']}个")
        
    except Exception as e:
        print(f"❌ 加载自定义配置失败: {e}")
        print("使用默认配置...")
        config = {
            "backtest": {
                "starting_balance": 10000
            },
            "bot": {
                "long": {
                    "entry_grid_spacing_pct": 0.01,  # 1%网格间距
                    "close_grid_markup_start": 0.005,  # 0.5%止盈
                    "entry_initial_qty_pct": 0.1,  # 每次用10%资金
                    "n_positions": 5  # 最多5个仓位
                }
            }
        }
    
    print("\n3. 运行回测...")
    result = simple_grid_strategy_backtest(ohlcv_data, config)
    
    print("\n4. 显示结果...")
    print_backtest_results(result)
    
    print("\n5. 保存结果...")
    with open('backtest_result.json', 'w') as f:
        # 转换numpy类型以便JSON序列化
        json_result = {}
        for key, value in result.items():
            if key == 'trades':
                json_result[key] = []
                for trade in value:
                    json_trade = {}
                    for k, v in trade.items():
                        if isinstance(v, (np.integer, np.floating)):
                            json_trade[k] = float(v)
                        elif isinstance(v, pd.Timestamp):
                            json_trade[k] = v.isoformat()
                        else:
                            json_trade[k] = v
                    json_result[key].append(json_trade)
            else:
                if isinstance(value, (np.integer, np.floating)):
                    json_result[key] = float(value)
                else:
                    json_result[key] = value
        
        json.dump(json_result, f, indent=2)
    
    print("回测结果已保存到: backtest_result.json")
    
    print("\n" + "="*50)
    print("回测完成！")
    print("="*50)

if __name__ == "__main__":
    main()
