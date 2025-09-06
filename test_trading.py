#!/usr/bin/env python3
"""
测试实盘交易功能
"""

import json
import os
import sys
from pathlib import Path

def test_trading_setup():
    """测试实盘交易设置"""
    
    print("🧪 测试实盘交易设置")
    print("=" * 50)
    
    # 检查配置文件
    config_path = Path("my_config.json")
    if not config_path.exists():
        print("❌ 配置文件不存在")
        return False
    
    # 检查API密钥文件
    api_keys_path = Path("api-keys.json")
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
        
        # 检查配置完整性
        issues = []
        
        # 1. 检查live配置
        if "live" not in config:
            issues.append("缺少live配置")
        else:
            live = config["live"]
            
            # 检查用户配置
            user = live.get("user")
            if not user:
                issues.append("缺少用户配置")
            elif user not in api_keys:
                issues.append(f"用户 '{user}' 在API密钥中不存在")
            else:
                print(f"✅ 用户配置: {user}")
                
                # 检查API密钥配置
                user_config = api_keys[user]
                if "exchange" not in user_config:
                    issues.append("API密钥中缺少交易所配置")
                else:
                    print(f"✅ 交易所: {user_config['exchange']}")
                
                if "key" not in user_config:
                    issues.append("API密钥中缺少key")
                else:
                    print(f"✅ API Key: {user_config['key'][:8]}...")
                
                if "secret" not in user_config:
                    issues.append("API密钥中缺少secret")
                else:
                    print(f"✅ Secret: {user_config['secret'][:8]}...")
            
            # 检查交易对配置
            approved_coins = live.get("approved_coins", [])
            if not approved_coins:
                issues.append("没有配置交易对")
            else:
                print(f"✅ 交易对: {approved_coins}")
            
            # 检查杠杆配置
            leverage = live.get("leverage", 1.0)
            if leverage > 10:
                print(f"⚠️ 杠杆倍数较高: {leverage}")
            else:
                print(f"✅ 杠杆倍数: {leverage}")
        
        # 2. 检查bot配置
        if "bot" not in config:
            issues.append("缺少bot配置")
        else:
            bot = config["bot"]
            if "long" not in bot:
                issues.append("缺少多头策略配置")
            else:
                print("✅ 多头策略配置存在")
            
            if "short" not in bot:
                issues.append("缺少空头策略配置")
            else:
                print("✅ 空头策略配置存在")
        
        # 3. 检查backtest配置
        if "backtest" not in config:
            issues.append("缺少backtest配置")
        else:
            backtest = config["backtest"]
            exchanges = backtest.get("exchanges", [])
            if not exchanges:
                issues.append("没有配置交易所")
            else:
                print(f"✅ 回测交易所: {exchanges}")
        
        # 显示结果
        if issues:
            print(f"\n❌ 发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"\n✅ 所有配置检查通过！")
            print(f"💡 可以尝试启动实盘交易")
            return True
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def test_python_imports():
    """测试Python模块导入"""
    
    print("\n🧪 测试Python模块导入")
    print("=" * 30)
    
    try:
        # 测试主要模块
        import ccxt
        print("✅ ccxt 模块导入成功")
        
        import pandas as pd
        print("✅ pandas 模块导入成功")
        
        import numpy as np
        print("✅ numpy 模块导入成功")
        
        # 测试Passivbot模块
        sys.path.insert(0, 'src')
        
        try:
            import passivbot
            print("✅ passivbot 模块导入成功")
        except ImportError as e:
            print(f"⚠️ passivbot 模块导入失败: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Passivbot 实盘交易测试")
    print("=" * 50)
    
    # 测试配置
    config_ok = test_trading_setup()
    
    # 测试Python模块
    imports_ok = test_python_imports()
    
    print("\n" + "=" * 50)
    if config_ok and imports_ok:
        print("✅ 所有测试通过！可以启动实盘交易")
        print("💡 使用命令: ./quick_start.sh trade")
    else:
        print("❌ 存在问题，请先修复后再启动实盘交易")