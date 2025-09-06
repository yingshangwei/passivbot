#!/usr/bin/env python3
"""
Passivbot 增强版Web服务器
支持配置保存、回测执行和结果展示
"""

import http.server
import socketserver
import json
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import tempfile
import shutil

class PassivbotHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP处理器"""
    
    def __init__(self, *args, **kwargs):
        # 设置项目根目录
        self.project_root = Path(__file__).parent.parent
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_file('index.html')
        elif path == '/api/status':
            self.handle_status()
        elif path == '/api/backtest/results':
            self.handle_backtest_results()
        elif path == '/api/config/status':
            self.handle_config_status()
        elif path == '/api/config/use-web':
            self.handle_use_web_config()
        elif path == '/api/config/backup':
            self.handle_backup_config()
        else:
            super().do_GET()
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/save-config':
            self.handle_save_config()
        elif path == '/api/run-backtest':
            self.handle_run_backtest()
        elif path == '/api/config/set-active':
            self.handle_set_active_config()
        else:
            self.send_error(404, "Not Found")
    
    def serve_file(self, filename):
        """提供文件服务"""
        try:
            file_path = Path(filename)
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "File not found")
        except Exception as e:
            self.send_error(500, f"Server error: {e}")
    
    def handle_status(self):
        """处理状态查询"""
        try:
            status = {
                "status": "running",
                "project_root": str(self.project_root),
                "config_exists": (self.project_root / "my_config.json").exists(),
                "backtest_dir": str(self.project_root / "backtests" / "combined")
            }
            
            self.send_json_response(status)
        except Exception as e:
            self.send_error(500, f"Status error: {e}")
    
    def handle_save_config(self):
        """处理配置保存"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config_data = json.loads(post_data.decode('utf-8'))
            
            # 保存配置文件
            config_path = self.project_root / "my_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            response = {
                "success": True,
                "message": "配置已保存到服务器",
                "path": str(config_path)
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            response = {
                "success": False,
                "message": f"保存配置失败: {e}"
            }
            self.send_json_response(response, 500)
    
    def handle_run_backtest(self):
        """处理回测执行"""
        try:
            # 检查配置文件是否存在
            config_path = self.project_root / "my_config.json"
            if not config_path.exists():
                response = {
                    "success": False,
                    "message": "配置文件不存在，请先保存配置"
                }
                self.send_json_response(response, 400)
                return
            
            # 在后台线程中执行回测
            def run_backtest_thread():
                try:
                    # 切换到项目目录
                    os.chdir(self.project_root)
                    
                    # 激活虚拟环境并运行回测
                    cmd = [
                        "bash", "-c",
                        "source venv/bin/activate && ./quick_start.sh backtest"
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5分钟超时
                    )
                    
                    # 保存回测结果
                    self.save_backtest_result(result)
                    
                except subprocess.TimeoutExpired:
                    self.save_backtest_result(None, "回测超时")
                except Exception as e:
                    self.save_backtest_result(None, f"回测执行失败: {e}")
            
            # 启动后台线程
            thread = threading.Thread(target=run_backtest_thread)
            thread.daemon = True
            thread.start()
            
            response = {
                "success": True,
                "message": "回测已开始执行，请稍后查看结果"
            }
            self.send_json_response(response)
            
        except Exception as e:
            response = {
                "success": False,
                "message": f"启动回测失败: {e}"
            }
            self.send_json_response(response, 500)
    
    def handle_backtest_results(self):
        """处理回测结果查询"""
        try:
            results = self.get_backtest_results()
            self.send_json_response(results)
        except Exception as e:
            self.send_error(500, f"获取回测结果失败: {e}")
    
    def save_backtest_result(self, result, error_msg=None):
        """保存回测结果"""
        try:
            result_data = {
                "timestamp": time.time(),
                "success": result is not None and result.returncode == 0,
                "error": error_msg,
                "stdout": result.stdout if result else "",
                "stderr": result.stderr if result else ""
            }
            
            # 保存到临时文件
            result_file = self.project_root / "web_config" / "last_backtest_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存回测结果失败: {e}")
    
    def get_backtest_results(self):
        """获取回测结果"""
        try:
            # 读取最新的回测结果
            result_file = self.project_root / "web_config" / "last_backtest_result.json"
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
            else:
                result_data = {
                    "timestamp": 0,
                    "success": False,
                    "error": "暂无回测结果",
                    "stdout": "",
                    "stderr": ""
                }
            
            # 获取最新的回测数据文件
            backtest_dir = self.project_root / "backtests" / "combined"
            latest_backtest = None
            analysis_data = None
            
            if backtest_dir.exists():
                subdirs = [d for d in backtest_dir.iterdir() if d.is_dir()]
                if subdirs:
                    latest_backtest = max(subdirs, key=os.path.getctime)
                    analysis_file = latest_backtest / "analysis.json"
                    if analysis_file.exists():
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            analysis_data = json.load(f)
            
            return {
                "execution": result_data,
                "latest_backtest": str(latest_backtest) if latest_backtest else None,
                "analysis": analysis_data
            }
            
        except Exception as e:
            return {
                "execution": {"error": f"获取结果失败: {e}"},
                "latest_backtest": None,
                "analysis": None
            }
    
    def handle_config_status(self):
        """处理配置状态查询"""
        try:
            status = {
                "local_config": {
                    "exists": (self.project_root / "my_config.json").exists(),
                    "path": str(self.project_root / "my_config.json"),
                    "modified": None,
                    "size": 0
                },
                "web_config": {
                    "exists": (self.project_root / "web_config" / "my_config.json").exists(),
                    "path": str(self.project_root / "web_config" / "my_config.json"),
                    "modified": None,
                    "size": 0
                },
                "backups": []
            }
            
            # 获取本地配置信息
            local_config_path = self.project_root / "my_config.json"
            if local_config_path.exists():
                stat_info = local_config_path.stat()
                status["local_config"]["modified"] = stat_info.st_mtime
                status["local_config"]["size"] = stat_info.st_size
            
            # 获取网页配置信息
            web_config_path = self.project_root / "web_config" / "my_config.json"
            if web_config_path.exists():
                stat_info = web_config_path.stat()
                status["web_config"]["modified"] = stat_info.st_mtime
                status["web_config"]["size"] = stat_info.st_size
            
            # 获取备份文件列表
            backup_pattern = self.project_root / "config_backup_*.json"
            import glob
            backup_files = glob.glob(str(backup_pattern))
            for backup_file in sorted(backup_files, reverse=True)[:10]:  # 最多显示10个
                backup_path = Path(backup_file)
                stat_info = backup_path.stat()
                status["backups"].append({
                    "name": backup_path.name,
                    "path": str(backup_path),
                    "modified": stat_info.st_mtime,
                    "size": stat_info.st_size
                })
            
            # 解析配置参数
            status["config_details"] = self.parse_config_details(status)
            
            self.send_json_response(status)
            
        except Exception as e:
            self.send_error(500, f"获取配置状态失败: {e}")
    
    def handle_use_web_config(self):
        """处理使用网页配置请求"""
        try:
            web_config_path = self.project_root / "web_config" / "my_config.json"
            local_config_path = self.project_root / "my_config.json"
            
            if not web_config_path.exists():
                response = {
                    "success": False,
                    "message": "网页服务配置文件不存在"
                }
                self.send_json_response(response, 400)
                return
            
            # 备份当前配置
            if local_config_path.exists():
                import shutil
                backup_file = self.project_root / f"config_backup_{int(time.time())}.json"
                shutil.copy2(local_config_path, backup_file)
            
            # 复制网页配置到本地
            import shutil
            shutil.copy2(web_config_path, local_config_path)
            
            response = {
                "success": True,
                "message": "已使用网页服务配置",
                "backup_created": local_config_path.exists()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            response = {
                "success": False,
                "message": f"使用网页配置失败: {e}"
            }
            self.send_json_response(response, 500)
    
    def handle_backup_config(self):
        """处理备份配置请求"""
        try:
            local_config_path = self.project_root / "my_config.json"
            
            if not local_config_path.exists():
                response = {
                    "success": False,
                    "message": "没有配置文件可备份"
                }
                self.send_json_response(response, 400)
                return
            
            # 创建备份
            import shutil
            backup_file = self.project_root / f"config_backup_{int(time.time())}.json"
            shutil.copy2(local_config_path, backup_file)
            
            response = {
                "success": True,
                "message": "配置已备份",
                "backup_file": str(backup_file)
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            response = {
                "success": False,
                "message": f"备份配置失败: {e}"
            }
            self.send_json_response(response, 500)
    
    def handle_set_active_config(self):
        """处理设置活动配置请求"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            config_source = data.get('source', 'web')  # 'web' or 'local'
            
            if config_source == 'web':
                # 使用网页配置
                web_config_path = self.project_root / "web_config" / "my_config.json"
                local_config_path = self.project_root / "my_config.json"
                
                if not web_config_path.exists():
                    response = {
                        "success": False,
                        "message": "网页服务配置文件不存在"
                    }
                    self.send_json_response(response, 400)
                    return
                
                # 备份当前配置
                if local_config_path.exists():
                    import shutil
                    backup_file = self.project_root / f"config_backup_{int(time.time())}.json"
                    shutil.copy2(local_config_path, backup_file)
                
                # 复制网页配置
                import shutil
                shutil.copy2(web_config_path, local_config_path)
                
                response = {
                    "success": True,
                    "message": "已设置网页配置为活动配置"
                }
            else:
                response = {
                    "success": False,
                    "message": "不支持的配置源"
                }
                self.send_json_response(response, 400)
                return
            
            self.send_json_response(response)
            
        except Exception as e:
            response = {
                "success": False,
                "message": f"设置活动配置失败: {e}"
            }
            self.send_json_response(response, 500)
    
    def parse_config_details(self, status):
        """解析配置参数详情"""
        details = {
            "local_config": None,
            "web_config": None
        }
        
        try:
            # 解析本地配置
            if status["local_config"]["exists"]:
                local_config_path = self.project_root / "my_config.json"
                with open(local_config_path, 'r', encoding='utf-8') as f:
                    local_config = json.load(f)
                details["local_config"] = self.extract_config_summary(local_config)
            
            # 解析网页配置
            if status["web_config"]["exists"]:
                web_config_path = self.project_root / "web_config" / "my_config.json"
                with open(web_config_path, 'r', encoding='utf-8') as f:
                    web_config = json.load(f)
                details["web_config"] = self.extract_config_summary(web_config)
                
        except Exception as e:
            print(f"解析配置详情失败: {e}")
        
        return details
    
    def extract_config_summary(self, config):
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
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))

def start_enhanced_server(port=8080):
    """启动增强版服务器"""
    
    # 切换到web_config目录
    web_config_dir = Path(__file__).parent
    os.chdir(web_config_dir)
    
    # 检查必要文件
    if not (web_config_dir / "index.html").exists():
        print("❌ 错误: index.html 文件不存在")
        return False
    
    try:
        with socketserver.TCPServer(("", port), PassivbotHandler) as httpd:
            print("🚀 Passivbot 增强版Web服务器启动成功!")
            print(f"📱 访问地址: http://localhost:{port}")
            print(f"📁 服务目录: {web_config_dir}")
            print("💡 新功能:")
            print("   ✅ 配置保存到服务器")
            print("   ✅ 在线执行回测")
            print("   ✅ 实时查看回测结果")
            print("   ✅ 自动盈利分析")
            print("\n⚠️  重要提醒:")
            print("   - 回测执行需要较长时间，请耐心等待")
            print("   - 建议先小资金测试策略")
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
            return start_enhanced_server(port + 1)
        else:
            print(f"❌ 启动服务器失败: {e}")
            return False
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        return True

def main():
    """主函数"""
    print("🤖 Passivbot 增强版Web服务器")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        return 1
    
    # 启动服务器
    if start_enhanced_server():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())