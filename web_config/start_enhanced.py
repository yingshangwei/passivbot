#!/usr/bin/env python3
"""
启动增强版Passivbot Web服务器
"""

import os
import sys
import shutil
from pathlib import Path

def setup_enhanced_server():
    """设置增强版服务器"""
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 复制增强版文件
    enhanced_index = current_dir / "enhanced_index.html"
    enhanced_server = current_dir / "enhanced_server.py"
    
    if enhanced_index.exists() and enhanced_server.exists():
        # 备份原文件
        if (current_dir / "index.html").exists():
            shutil.copy2(current_dir / "index.html", current_dir / "index_backup.html")
        
        # 使用增强版文件
        shutil.copy2(enhanced_index, current_dir / "index.html")
        
        print("✅ 增强版文件已设置")
        return True
    else:
        print("❌ 增强版文件不存在")
        return False

def start_server():
    """启动服务器"""
    try:
        # 导入并运行增强版服务器
        sys.path.insert(0, str(Path(__file__).parent))
        from enhanced_server import main
        return main()
    except ImportError as e:
        print(f"❌ 导入增强版服务器失败: {e}")
        return 1
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return 1

def main():
    """主函数"""
    print("🤖 Passivbot 增强版Web服务器启动器")
    print("=" * 50)
    
    # 设置增强版服务器
    if not setup_enhanced_server():
        return 1
    
    # 启动服务器
    return start_server()

if __name__ == "__main__":
    sys.exit(main())