#!/usr/bin/env python3
"""
Passivbot 配置网页服务器
简单的HTTP服务器，用于提供配置网页界面
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_server(port=8080):
    """启动配置网页服务器"""
    
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # 检查index.html是否存在
    if not (current_dir / "index.html").exists():
        print("❌ 错误: index.html 文件不存在")
        print(f"请确保 {current_dir / 'index.html'} 文件存在")
        return False
    
    # 创建HTTP服务器
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print("🚀 Passivbot 配置网页服务器启动成功!")
            print(f"📱 访问地址: http://localhost:{port}")
            print(f"📁 服务目录: {current_dir}")
            print("💡 使用说明:")
            print("   1. 在网页中选择预设配置或自定义参数")
            print("   2. 点击'生成配置'按钮")
            print("   3. 复制或下载生成的配置文件")
            print("   4. 将配置文件保存为 my_config.json")
            print("   5. 使用 ./quick_start.sh 启动交易")
            print("\n⚠️  重要提醒:")
            print("   - 请确保充分理解参数含义后再进行实盘交易")
            print("   - 建议先小资金测试")
            print("   - 定期监控交易状态")
            print("\n按 Ctrl+C 停止服务器")
            print("-" * 50)
            
            # 自动打开浏览器
            try:
                webbrowser.open(f"http://localhost:{port}")
                print("🌐 已自动打开浏览器")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print(f"请手动访问: http://localhost:{port}")
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {port} 已被占用，尝试使用端口 {port + 1}")
            return start_server(port + 1)
        else:
            print(f"❌ 启动服务器失败: {e}")
            return False
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        return True

def main():
    """主函数"""
    print("🤖 Passivbot 配置网页服务器")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        return 1
    
    # 启动服务器
    if start_server():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())