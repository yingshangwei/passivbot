#!/usr/bin/env python3
"""
简单回测演示

这个脚本演示了如何使用Passivbot的回测功能，使用模拟数据。
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_mock_ohlcv_data(symbol: str, start_date: str, end_date: str, interval: str = '1m'):
    """
    创建模拟的OHLCV数据
    
    Args:
        symbol: 交易对符号
        start_date: 开始日期
        end_date: 结束日期
        interval: 时间间隔
        
    Returns:
        pandas.DataFrame: OHLCV数据
    """
    print(f"创建模拟数据: {symbol} from {start_date} to {end_date}")
    
    # 解析日期
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 生成时间序列
    if interval == '1m':
        freq = '1T'
    elif interval == '1h':
        freq = '1H'
    else:
        freq = '1T'
    
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

def save_ohlcv_data(df: pd.DataFrame, exchange: str, symbol: str, base_dir: str = "backtests"):
    """
    保存OHLCV数据到文件
    
    Args:
        df: OHLCV数据DataFrame
        exchange: 交易所名称
        symbol: 交易对符号
        base_dir: 基础目录
    """
    # 创建目录结构
    data_dir = os.path.join(base_dir, exchange, symbol, "caches")
    os.makedirs(data_dir, exist_ok=True)
    
    # 保存为numpy格式（Passivbot期望的格式）
    ohlcv_array = df[['open', 'high', 'low', 'close', 'volume']].values
    np.save(os.path.join(data_dir, "ohlcvs_1m.npy"), ohlcv_array)
    
    # 保存时间戳
    timestamps = df.index.astype(np.int64) // 10**6  # 转换为毫秒时间戳
    np.save(os.path.join(data_dir, "timestamps_1m.npy"), timestamps)
    
    print(f"数据已保存到: {data_dir}")

def create_simple_backtest_config():
    """创建简单的回测配置"""
    config = {
        "backtest": {
            "base_dir": "backtests",
            "combine_ohlcvs": True,
            "compress_cache": False,
            "end_date": "2024-01-31",
            "exchanges": ["binance"],
            "gap_tolerance_ohlcvs_minutes": 120,
            "start_date": "2024-01-01",
            "starting_balance": 10000,
            "use_btc_collateral": True
        },
        "bot": {
            "long": {
                "close_grid_markup_end": 0.003,
                "close_grid_markup_start": 0.006,
                "close_grid_qty_pct": 0.94,
                "close_trailing_grid_ratio": -0.006,
                "close_trailing_qty_pct": 0.27,
                "close_trailing_retracement_pct": 0.0007,
                "close_trailing_threshold_pct": 0.051,
                "ema_span_0": 279,
                "ema_span_1": 476,
                "enforce_exposure_limit": True,
                "entry_grid_double_down_factor": 0.85,
                "entry_grid_spacing_pct": 0.027,
                "entry_grid_spacing_weight": 0.31,
                "entry_initial_ema_dist": -0.004,
                "entry_initial_qty_pct": 0.016,
                "entry_trailing_double_down_factor": 3.04,
                "entry_trailing_grid_ratio": 0.007,
                "entry_trailing_retracement_pct": 0.014,
                "entry_trailing_threshold_pct": 0.065,
                "filter_noisiness_rolling_window": 40,
                "filter_volume_drop_pct": 0.51,
                "filter_volume_rolling_window": 1886,
                "n_positions": 7,
                "total_wallet_exposure_limit": 2,
                "unstuck_close_pct": 0.041,
                "unstuck_ema_dist": 0.003,
                "unstuck_loss_allowance_pct": 0.002,
                "unstuck_threshold": 0.68
            },
            "short": {
                "close_grid_markup_end": 0.002,
                "close_grid_markup_start": 0.020,
                "close_grid_qty_pct": 0.052,
                "close_trailing_grid_ratio": -0.127,
                "close_trailing_qty_pct": 0.074,
                "close_trailing_retracement_pct": 0.004,
                "close_trailing_threshold_pct": -0.009,
                "ema_span_0": 1365,
                "ema_span_1": 985,
                "enforce_exposure_limit": True,
                "entry_grid_double_down_factor": 3.41,
                "entry_grid_spacing_pct": 0.037,
                "entry_grid_spacing_weight": 1.66,
                "entry_initial_ema_dist": 0.004,
                "entry_initial_qty_pct": 0.016,
                "entry_trailing_double_down_factor": 3.04,
                "entry_trailing_grid_ratio": 0.007,
                "entry_trailing_retracement_pct": 0.014,
                "entry_trailing_threshold_pct": 0.065,
                "filter_noisiness_rolling_window": 40,
                "filter_volume_drop_pct": 0.51,
                "filter_volume_rolling_window": 1886,
                "n_positions": 7,
                "total_wallet_exposure_limit": 2,
                "unstuck_close_pct": 0.041,
                "unstuck_ema_dist": 0.003,
                "unstuck_loss_allowance_pct": 0.002,
                "unstuck_threshold": 0.68
            }
        },
        "live": {
            "approved_coins": ["BTCUSDT"],
            "auto_gs": False,
            "empty_means_all_approved": False,
            "execution_delay_seconds": 0.0,
            "filter_by_min_effective_cost": False,
            "forced_mode_long": "n",
            "forced_mode_short": "n",
            "ignored_coins": {
                "long": [],
                "short": []
            },
            "leverage": 1.0,
            "market_orders_allowed": False,
            "max_n_cancellations_per_batch": 100,
            "max_n_creations_per_batch": 100,
            "max_n_restarts_per_day": 10,
            "mimic_backtest_1m_delay": False,
            "minimum_coin_age_days": 30,
            "ohlcvs_1m_rolling_window_days": 7,
            "ohlcvs_1m_update_after_minutes": 1,
            "pnls_max_lookback_days": 30,
            "price_distance_threshold": 0.002,
            "time_in_force": "GTC",
            "user": "test_user"
        }
    }
    
    return config

def main():
    """主函数"""
    print("Passivbot 简单回测演示")
    print("=" * 50)
    
    # 创建模拟数据
    symbol = "BTCUSDT"
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    print("1. 创建模拟OHLCV数据...")
    ohlcv_data = create_mock_ohlcv_data(symbol, start_date, end_date)
    
    print("\n2. 保存数据到文件...")
    save_ohlcv_data(ohlcv_data, "binance", symbol)
    
    print("\n3. 创建回测配置...")
    config = create_simple_backtest_config()
    
    # 保存配置文件
    import json
    config_file = "simple_backtest_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"配置文件已保存: {config_file}")
    
    print("\n4. 数据准备完成！")
    print("现在可以运行回测:")
    print(f"python src/backtest.py {config_file} --disable_plotting")
    
    print("\n5. 数据概览:")
    print(f"数据点数: {len(ohlcv_data)}")
    print(f"时间范围: {ohlcv_data.index[0]} 到 {ohlcv_data.index[-1]}")
    print(f"价格统计:")
    print(f"  开盘价: {ohlcv_data['open'].mean():.2f} ± {ohlcv_data['open'].std():.2f}")
    print(f"  收盘价: {ohlcv_data['close'].mean():.2f} ± {ohlcv_data['close'].std():.2f}")
    print(f"  最高价: {ohlcv_data['high'].max():.2f}")
    print(f"  最低价: {ohlcv_data['low'].min():.2f}")
    print(f"  平均成交量: {ohlcv_data['volume'].mean():.2f}")

if __name__ == "__main__":
    main()
