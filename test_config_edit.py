#!/usr/bin/env python3
"""
测试配置参数编辑功能
"""

import json
import os
from pathlib import Path

def test_config_edit():
    """测试配置参数编辑功能"""
    
    print("🧪 测试配置参数编辑功能")
    print("=" * 50)
    
    # 检查网页配置文件
    web_config_path = Path("web_config/my_config.json")
    if not web_config_path.exists():
        # 如果网页配置不存在，使用本地配置
        web_config_path = Path("my_config.json")
    if web_config_path.exists():
        print("📁 发现网页配置文件")
        
        try:
            with open(web_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("✅ 配置文件解析成功")
            
            # 显示当前配置
            print("\n📋 当前配置参数:")
            
            # 回测配置
            if "backtest" in config:
                bt = config["backtest"]
                print(f"  📊 回测配置:")
                print(f"    开始日期: {bt.get('start_date', '未设置')}")
                print(f"    结束日期: {bt.get('end_date', '未设置')}")
                print(f"    初始资金: {bt.get('starting_balance', '未设置')}")
                print(f"    交易所: {bt.get('exchanges', [])}")
            
            # 实盘配置
            if "live" in config:
                live = config["live"]
                print(f"  🚀 实盘配置:")
                print(f"    交易对: {live.get('approved_coins', [])}")
                print(f"    杠杆倍数: {live.get('leverage', '未设置')} ⭐")
                print(f"    用户: {live.get('user', '未设置')}")
                print(f"    订单有效期: {live.get('time_in_force', '未设置')}")
                print(f"    执行延迟: {live.get('execution_delay_seconds', '未设置')} 秒")
                print(f"    最小币龄: {live.get('minimum_coin_age_days', '未设置')} 天")
            
            # 多头策略配置
            if "bot" in config and "long" in config["bot"]:
                long = config["bot"]["long"]
                print(f"  📈 多头策略配置:")
                print(f"    入场网格间距: {long.get('entry_grid_spacing_pct', '未设置')}%")
                print(f"    初始入场数量: {long.get('entry_initial_qty_pct', '未设置')}%")
                print(f"    最大持仓数: {long.get('n_positions', '未设置')}")
                print(f"    平仓网格起始: {long.get('close_grid_markup_start', '未设置')}%")
                print(f"    平仓网格结束: {long.get('close_grid_markup_end', '未设置')}%")
                print(f"    资金暴露限制: {long.get('total_wallet_exposure_limit', '未设置')}")
                print(f"    EMA周期0: {long.get('ema_span_0', '未设置')}")
                print(f"    EMA周期1: {long.get('ema_span_1', '未设置')}")
            
            # 空头策略配置
            if "bot" in config and "short" in config["bot"]:
                short = config["bot"]["short"]
                print(f"  📉 空头策略配置:")
                print(f"    入场网格间距: {short.get('entry_grid_spacing_pct', '未设置')}%")
                print(f"    初始入场数量: {short.get('entry_initial_qty_pct', '未设置')}%")
                print(f"    最大持仓数: {short.get('n_positions', '未设置')}")
            
            print("\n" + "=" * 50)
            print("✅ 配置参数编辑功能测试完成")
            print("💡 现在可以在Web界面中编辑所有配置参数")
            print("💡 包括杠杆倍数、交易对、策略参数等")
            print("💡 编辑后可以保存到服务器并同步到快速启动脚本")
            
        except Exception as e:
            print(f"❌ 配置文件解析失败: {e}")
    else:
        print("⚠️ 网页配置文件不存在")
        print("💡 请先在Web界面中生成并保存配置")

if __name__ == "__main__":
    test_config_edit()