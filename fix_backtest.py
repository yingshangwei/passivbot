#!/usr/bin/env python3
"""
Passivbot 回测修复脚本
解决常见的回测问题
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timedelta

def print_status(message, status="INFO"):
    """打印状态信息"""
    colors = {
        "INFO": "\033[0;32m",
        "WARNING": "\033[1;33m", 
        "ERROR": "\033[0;31m",
        "SUCCESS": "\033[0;32m"
    }
    print(f"{colors.get(status, '')}[{status}]\033[0m {message}")

def check_network():
    """检查网络连接"""
    try:
        import requests
        response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_simple_config():
    """创建简单的配置文件"""
    config = {
        "backtest": {
            "base_dir": "backtests",
            "combine_ohlcvs": True,
            "compress_cache": True,
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "starting_balance": 10000,
            "exchanges": ["binance"],
            "gap_tolerance_ohlcvs_minutes": 120,
            "use_btc_collateral": True
        },
        "bot": {
            "long": {
                "close_grid_markup_end": 0.001,
                "close_grid_markup_start": 0.002,
                "close_grid_qty_pct": 0.5,
                "close_trailing_grid_ratio": 0.0,
                "close_trailing_qty_pct": 0.0,
                "close_trailing_retracement_pct": 0.0,
                "close_trailing_threshold_pct": 0.0,
                "ema_span_0": 100,
                "ema_span_1": 200,
                "enforce_exposure_limit": True,
                "entry_grid_double_down_factor": 1.0,
                "entry_grid_spacing_pct": 0.01,
                "entry_grid_spacing_weight": 1.0,
                "entry_initial_ema_dist": 0.0,
                "entry_initial_qty_pct": 0.01,
                "entry_trailing_double_down_factor": 1.0,
                "entry_trailing_grid_ratio": 0.0,
                "entry_trailing_retracement_pct": 0.0,
                "entry_trailing_threshold_pct": 0.0,
                "filter_noisiness_rolling_window": 20,
                "filter_volume_drop_pct": 0.0,
                "filter_volume_rolling_window": 100,
                "n_positions": 3,
                "total_wallet_exposure_limit": 0.5,
                "unstuck_close_pct": 0.01,
                "unstuck_ema_dist": 0.001,
                "unstuck_loss_allowance_pct": 0.001,
                "unstuck_threshold": 0.5
            },
            "short": {
                "close_grid_markup_end": 0.001,
                "close_grid_markup_start": 0.002,
                "close_grid_qty_pct": 0.5,
                "close_trailing_grid_ratio": 0.0,
                "close_trailing_qty_pct": 0.0,
                "close_trailing_retracement_pct": 0.0,
                "close_trailing_threshold_pct": 0.0,
                "ema_span_0": 100,
                "ema_span_1": 200,
                "enforce_exposure_limit": True,
                "entry_grid_double_down_factor": 1.0,
                "entry_grid_spacing_pct": 0.01,
                "entry_grid_spacing_weight": 1.0,
                "entry_initial_ema_dist": 0.0,
                "entry_initial_qty_pct": 0.01,
                "entry_trailing_double_down_factor": 1.0,
                "entry_trailing_grid_ratio": 0.0,
                "entry_trailing_retracement_pct": 0.0,
                "entry_trailing_threshold_pct": 0.0,
                "filter_noisiness_rolling_window": 20,
                "filter_volume_drop_pct": 0.0,
                "filter_volume_rolling_window": 100,
                "n_positions": 3,
                "total_wallet_exposure_limit": 0.5,
                "unstuck_close_pct": 0.01,
                "unstuck_ema_dist": 0.001,
                "unstuck_loss_allowance_pct": 0.001,
                "unstuck_threshold": 0.5
            }
        },
        "live": {
            "approved_coins": ["BTCUSDT"],
            "auto_gs": False,
            "empty_means_all_approved": False,
            "execution_delay_seconds": 0,
            "filter_by_min_effective_cost": False,
            "forced_mode_long": "n",
            "forced_mode_short": "n",
            "ignored_coins": {"long": [], "short": []},
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
    
    with open("my_config_simple.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print_status("已创建简单配置文件: my_config_simple.json", "SUCCESS")

def run_backtest_with_retry():
    """运行回测，带重试机制"""
    max_retries = 3
    
    for attempt in range(max_retries):
        print_status(f"尝试运行回测 (第 {attempt + 1}/{max_retries} 次)", "INFO")
        
        try:
            # 使用简单配置
            if os.path.exists("my_config_simple.json"):
                os.system("cp my_config_simple.json my_config.json")
            
            # 运行回测
            result = subprocess.run([
                "python", "src/backtest.py", 
                "--config", "my_config.json",
                "--start_date", "2024-01-01",
                "--end_date", "2024-01-31"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_status("回测成功完成！", "SUCCESS")
                print(result.stdout)
                return True
            else:
                print_status(f"回测失败: {result.stderr}", "ERROR")
                if attempt < max_retries - 1:
                    print_status("等待5秒后重试...", "WARNING")
                    time.sleep(5)
                    
        except subprocess.TimeoutExpired:
            print_status("回测超时，尝试更短的时间范围", "WARNING")
            # 尝试更短的时间范围
            config = json.load(open("my_config.json"))
            config["backtest"]["end_date"] = "2024-01-07"
            with open("my_config.json", "w") as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print_status(f"运行回测时出错: {e}", "ERROR")
    
    return False

def main():
    """主函数"""
    print_status("Passivbot 回测修复脚本", "INFO")
    print_status("=" * 50, "INFO")
    
    # 检查网络连接
    print_status("检查网络连接...", "INFO")
    if not check_network():
        print_status("网络连接失败，建议使用离线演示", "WARNING")
        print_status("运行: ./quick_start.sh demo", "INFO")
        return
    
    print_status("网络连接正常", "SUCCESS")
    
    # 创建简单配置
    print_status("创建简单配置文件...", "INFO")
    create_simple_config()
    
    # 运行回测
    print_status("开始运行回测...", "INFO")
    if run_backtest_with_retry():
        print_status("回测修复完成！", "SUCCESS")
    else:
        print_status("回测仍然失败，建议使用离线演示", "ERROR")
        print_status("运行: ./quick_start.sh demo", "INFO")

if __name__ == "__main__":
    main()