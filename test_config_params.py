#!/usr/bin/env python3
"""
测试配置参数解析功能
"""

import json
import os
from pathlib import Path

def extract_config_summary(config):
    """提取配置摘要信息"""
    summary = {
        "backtest": {},
        "bot": {"long": {}, "short": {}},
        "live": {}
    }
    
    try:
        # 回测配置
        if "backtest" in config:
            bt = config["backtest"]
            summary["backtest"] = {
                "start_date": bt.get("start_date", "未设置"),
                "end_date": bt.get("end_date", "未设置"),
                "starting_balance": bt.get("starting_balance", "未设置"),
                "exchanges": bt.get("exchanges", [])
            }
        
        # 机器人配置 - 多头
        if "bot" in config and "long" in config["bot"]:
            long_config = config["bot"]["long"]
            summary["bot"]["long"] = {
                "entry_grid_spacing_pct": long_config.get("entry_grid_spacing_pct", "未设置"),
                "entry_initial_qty_pct": long_config.get("entry_initial_qty_pct", "未设置"),
                "n_positions": long_config.get("n_positions", "未设置"),
                "close_grid_markup_start": long_config.get("close_grid_markup_start", "未设置"),
                "close_grid_markup_end": long_config.get("close_grid_markup_end", "未设置"),
                "total_wallet_exposure_limit": long_config.get("total_wallet_exposure_limit", "未设置"),
                "ema_span_0": long_config.get("ema_span_0", "未设置"),
                "ema_span_1": long_config.get("ema_span_1", "未设置")
            }
        
        # 机器人配置 - 空头
        if "bot" in config and "short" in config["bot"]:
            short_config = config["bot"]["short"]
            summary["bot"]["short"] = {
                "entry_grid_spacing_pct": short_config.get("entry_grid_spacing_pct", "未设置"),
                "entry_initial_qty_pct": short_config.get("entry_initial_qty_pct", "未设置"),
                "n_positions": short_config.get("n_positions", "未设置"),
                "close_grid_markup_start": short_config.get("close_grid_markup_start", "未设置"),
                "close_grid_markup_end": short_config.get("close_grid_markup_end", "未设置"),
                "total_wallet_exposure_limit": short_config.get("total_wallet_exposure_limit", "未设置"),
                "ema_span_0": short_config.get("ema_span_0", "未设置"),
                "ema_span_1": short_config.get("ema_span_1", "未设置")
            }
        
        # 实盘配置
        if "live" in config:
            live = config["live"]
            summary["live"] = {
                "approved_coins": live.get("approved_coins", []),
                "leverage": live.get("leverage", "未设置"),
                "user": live.get("user", "未设置"),
                "time_in_force": live.get("time_in_force", "未设置"),
                "execution_delay_seconds": live.get("execution_delay_seconds", "未设置"),
                "minimum_coin_age_days": live.get("minimum_coin_age_days", "未设置")
            }
            
    except Exception as e:
        print(f"提取配置摘要失败: {e}")
    
    return summary

def test_config_parsing():
    """测试配置参数解析"""
    
    print("🧪 测试配置参数解析功能")
    print("=" * 50)
    
    # 测试本地配置
    local_config_path = Path("../my_config.json")
    if local_config_path.exists():
        print("📁 测试本地配置文件...")
        try:
            with open(local_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            summary = extract_config_summary(config)
            
            print("✅ 本地配置解析成功")
            print("\n📋 配置参数详情:")
            
            # 回测配置
            if summary["backtest"]:
                print("\n📊 回测配置:")
                for key, value in summary["backtest"].items():
                    print(f"  {key}: {value}")
            
            # 多头策略配置
            if summary["bot"]["long"]:
                print("\n📈 多头策略配置:")
                for key, value in summary["bot"]["long"].items():
                    print(f"  {key}: {value}")
            
            # 空头策略配置
            if summary["bot"]["short"]:
                print("\n📉 空头策略配置:")
                for key, value in summary["bot"]["short"].items():
                    print(f"  {key}: {value}")
            
            # 实盘配置
            if summary["live"]:
                print("\n🚀 实盘配置:")
                for key, value in summary["live"].items():
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print(f"❌ 本地配置解析失败: {e}")
    else:
        print("⚠️ 本地配置文件不存在")
    
    # 测试网页配置
    web_config_path = Path("my_config.json")
    if web_config_path.exists():
        print("\n📁 测试网页配置文件...")
        try:
            with open(web_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            summary = extract_config_summary(config)
            
            print("✅ 网页配置解析成功")
            print("\n📋 配置参数详情:")
            
            # 回测配置
            if summary["backtest"]:
                print("\n📊 回测配置:")
                for key, value in summary["backtest"].items():
                    print(f"  {key}: {value}")
            
            # 多头策略配置
            if summary["bot"]["long"]:
                print("\n📈 多头策略配置:")
                for key, value in summary["bot"]["long"].items():
                    print(f"  {key}: {value}")
            
            # 空头策略配置
            if summary["bot"]["short"]:
                print("\n📉 空头策略配置:")
                for key, value in summary["bot"]["short"].items():
                    print(f"  {key}: {value}")
            
            # 实盘配置
            if summary["live"]:
                print("\n🚀 实盘配置:")
                for key, value in summary["live"].items():
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print(f"❌ 网页配置解析失败: {e}")
    else:
        print("⚠️ 网页配置文件不存在")
    
    print("\n" + "=" * 50)
    print("✅ 配置参数解析功能测试完成")
    print("💡 现在Web界面将显示完整的配置参数详情")
    print("💡 包括杠杆倍数、交易对、策略参数等所有配置")

if __name__ == "__main__":
    test_config_parsing()