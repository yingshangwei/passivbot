#!/usr/bin/env python3
"""
测试配置参数展示功能
"""

import json
import requests
import time

def test_config_display():
    """测试配置参数展示功能"""
    
    base_url = "http://localhost:8080"
    
    print("🧪 测试配置参数展示功能")
    print("=" * 50)
    
    # 测试配置状态API
    try:
        print("1. 测试配置状态API...")
        response = requests.get(f"{base_url}/api/config/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 配置状态API正常")
            
            # 显示配置详情
            if data.get("config_details"):
                print("\n📋 配置参数详情:")
                
                # 本地配置
                if data["config_details"].get("local_config"):
                    print("\n💻 本地配置参数:")
                    local_config = data["config_details"]["local_config"]
                    
                    # 回测配置
                    if local_config.get("backtest"):
                        print("  📊 回测配置:")
                        for key, value in local_config["backtest"].items():
                            print(f"    {key}: {value}")
                    
                    # 多头策略配置
                    if local_config.get("bot", {}).get("long"):
                        print("  📈 多头策略配置:")
                        for key, value in local_config["bot"]["long"].items():
                            print(f"    {key}: {value}")
                    
                    # 空头策略配置
                    if local_config.get("bot", {}).get("short"):
                        print("  📉 空头策略配置:")
                        for key, value in local_config["bot"]["short"].items():
                            print(f"    {key}: {value}")
                    
                    # 实盘配置
                    if local_config.get("live"):
                        print("  🚀 实盘配置:")
                        for key, value in local_config["live"].items():
                            print(f"    {key}: {value}")
                
                # 网页配置
                if data["config_details"].get("web_config"):
                    print("\n🌐 网页配置参数:")
                    web_config = data["config_details"]["web_config"]
                    
                    # 回测配置
                    if web_config.get("backtest"):
                        print("  📊 回测配置:")
                        for key, value in web_config["backtest"].items():
                            print(f"    {key}: {value}")
                    
                    # 多头策略配置
                    if web_config.get("bot", {}).get("long"):
                        print("  📈 多头策略配置:")
                        for key, value in web_config["bot"]["long"].items():
                            print(f"    {key}: {value}")
                    
                    # 空头策略配置
                    if web_config.get("bot", {}).get("short"):
                        print("  📉 空头策略配置:")
                        for key, value in web_config["bot"]["short"].items():
                            print(f"    {key}: {value}")
                    
                    # 实盘配置
                    if web_config.get("live"):
                        print("  🚀 实盘配置:")
                        for key, value in web_config["live"].items():
                            print(f"    {key}: {value}")
            else:
                print("⚠️ 没有配置详情数据")
                
        else:
            print(f"❌ 配置状态API失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ 配置参数展示功能测试完成")
    print("💡 请在浏览器中访问 http://localhost:8080 查看完整界面")
    print("💡 切换到'配置工具'标签页查看配置参数详情")
    
    return True

if __name__ == "__main__":
    test_config_display()