#!/usr/bin/env python3
"""
修复实盘交易配置问题
"""

import json
import os
from pathlib import Path

def fix_trading_config():
    """修复实盘交易配置"""
    
    print("🔧 修复实盘交易配置")
    print("=" * 50)
    
    config_path = Path("my_config.json")
    api_keys_path = Path("api-keys.json")
    
    if not config_path.exists():
        print("❌ 配置文件不存在")
        return False
    
    if not api_keys_path.exists():
        print("❌ API密钥文件不存在")
        return False
    
    try:
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 读取API密钥文件
        with open(api_keys_path, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        print("✅ 配置文件读取成功")
        
        # 检查并修复配置问题
        issues_found = []
        fixes_applied = []
        
        # 1. 检查用户配置
        if "live" in config:
            live_config = config["live"]
            user = live_config.get("user", "")
            
            # 检查API密钥中是否有对应的用户
            if user not in api_keys:
                print(f"⚠️ 用户 '{user}' 在API密钥中不存在")
                # 使用第一个可用的用户
                available_users = [k for k in api_keys.keys() if k != "referrals"]
                if available_users:
                    new_user = available_users[0]
                    config["live"]["user"] = new_user
                    fixes_applied.append(f"用户设置: {user} -> {new_user}")
                    print(f"✅ 已修复用户设置: {new_user}")
                else:
                    issues_found.append("没有可用的API密钥用户")
            else:
                print(f"✅ 用户配置正确: {user}")
        
        # 2. 检查交易所配置
        if "backtest" in config and "exchanges" in config["backtest"]:
            exchange = config["backtest"]["exchanges"][0] if config["backtest"]["exchanges"] else ""
            user = config.get("live", {}).get("user", "")
            
            if user in api_keys:
                api_exchange = api_keys[user].get("exchange", "")
                if exchange != api_exchange:
                    config["backtest"]["exchanges"] = [api_exchange]
                    fixes_applied.append(f"交易所设置: {exchange} -> {api_exchange}")
                    print(f"✅ 已修复交易所设置: {api_exchange}")
                else:
                    print(f"✅ 交易所配置正确: {exchange}")
            else:
                issues_found.append("无法验证交易所配置")
        
        # 3. 检查执行延迟设置
        if "live" in config:
            execution_delay = config["live"].get("execution_delay_seconds")
            if execution_delay is None:
                config["live"]["execution_delay_seconds"] = 0
                fixes_applied.append("执行延迟: null -> 0")
                print("✅ 已修复执行延迟设置")
            else:
                print(f"✅ 执行延迟设置正确: {execution_delay}")
        
        # 4. 检查杠杆设置
        if "live" in config:
            leverage = config["live"].get("leverage", 1.0)
            if leverage > 10:
                print(f"⚠️ 杠杆倍数较高: {leverage}")
                print("💡 建议降低杠杆倍数以控制风险")
            else:
                print(f"✅ 杠杆设置: {leverage}")
        
        # 保存修复后的配置
        if fixes_applied:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ 已应用 {len(fixes_applied)} 个修复:")
            for fix in fixes_applied:
                print(f"  - {fix}")
        
        # 显示最终配置摘要
        print(f"\n📋 最终配置摘要:")
        if "live" in config:
            live = config["live"]
            print(f"  用户: {live.get('user', '未设置')}")
            print(f"  交易对: {live.get('approved_coins', [])}")
            print(f"  杠杆倍数: {live.get('leverage', '未设置')}")
            print(f"  执行延迟: {live.get('execution_delay_seconds', '未设置')} 秒")
        
        if "backtest" in config:
            bt = config["backtest"]
            print(f"  交易所: {bt.get('exchanges', [])}")
            print(f"  初始资金: {bt.get('starting_balance', '未设置')}")
        
        if issues_found:
            print(f"\n⚠️ 仍需注意的问题:")
            for issue in issues_found:
                print(f"  - {issue}")
        
        print(f"\n✅ 配置修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复配置时出错: {e}")
        return False

if __name__ == "__main__":
    fix_trading_config()