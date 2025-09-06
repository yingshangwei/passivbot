#!/bin/bash

# Passivbot 快速启动脚本
# 使用方法: ./quick_start.sh [命令]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/Users/shangwei.ying/workspace/git/passivbot"
VENV_PATH="$PROJECT_DIR/venv"

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Passivbot 快速启动脚本${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查环境
check_environment() {
    print_message "检查环境..."
    
    if [ ! -d "$VENV_PATH" ]; then
        print_error "虚拟环境不存在，请先运行部署脚本"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_DIR/api-keys.json" ]; then
        print_warning "API密钥文件不存在，请先配置"
        print_message "运行: cp api-keys.json.example api-keys.json"
        print_message "然后编辑 api-keys.json 文件"
    fi
    
    print_message "环境检查完成"
}

# 激活虚拟环境
activate_venv() {
    print_message "激活虚拟环境..."
    source "$VENV_PATH/bin/activate"
    print_message "虚拟环境已激活"
}

# 显示帮助信息
show_help() {
    print_header
    echo "使用方法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  help         显示此帮助信息"
    echo "  check        检查环境和依赖"
    echo "  config       配置向导"
    echo "  backtest     运行回测"
    echo "  optimize     运行优化器"
    echo "  trade        启动交易"
    echo "  monitor      监控交易状态"
    echo "  logs         查看日志"
    echo "  clean        清理临时文件"
    echo ""
    echo "示例:"
    echo "  $0 check     # 检查环境"
    echo "  $0 backtest  # 运行回测"
    echo "  $0 trade     # 启动交易"
}

# 配置向导
config_wizard() {
    print_header
    print_message "配置向导"
    
    # 检查API密钥
    if [ ! -f "$PROJECT_DIR/api-keys.json" ]; then
        print_message "创建API密钥文件..."
        cp "$PROJECT_DIR/api-keys.json.example" "$PROJECT_DIR/api-keys.json"
        print_warning "请编辑 api-keys.json 文件，添加您的API密钥"
    fi
    
    # 检查配置文件
    if [ ! -f "$PROJECT_DIR/my_config.json" ]; then
        print_message "创建配置文件..."
        cp "$PROJECT_DIR/configs/template.json" "$PROJECT_DIR/my_config.json"
        print_warning "请编辑 my_config.json 文件，配置交易参数"
    fi
    
    print_message "配置完成！"
    print_message "下一步: 编辑配置文件，然后运行回测"
}

# 运行回测
run_backtest() {
    print_header
    print_message "运行回测..."
    
    activate_venv
    cd "$PROJECT_DIR"
    
    if [ ! -f "my_config.json" ]; then
        print_error "配置文件不存在，请先运行配置向导"
        exit 1
    fi
    
    print_message "开始回测..."
    python src/backtest.py my_config.json --backtest.start_date 2024-01-01 --backtest.end_date 2024-06-01
    
    print_message "回测完成！"
    print_message "查看结果: ls -la backtests/"
}

# 运行优化器
run_optimize() {
    print_header
    print_message "运行优化器..."
    
    activate_venv
    cd "$PROJECT_DIR"
    
    if [ ! -f "my_config.json" ]; then
        print_error "配置文件不存在，请先运行配置向导"
        exit 1
    fi
    
    print_message "开始优化..."
    print_warning "优化过程可能需要较长时间..."
    python src/optimize.py my_config.json --optimize.iters 100 --optimize.population_size 20
    
    print_message "优化完成！"
    print_message "查看结果: ls -la backtests/*/optimize/"
}

# 启动交易
start_trading() {
    print_header
    print_warning "启动实盘交易..."
    print_warning "请确保您已经充分测试并了解风险！"
    
    read -p "确认启动实盘交易？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_message "已取消"
        exit 0
    fi
    
    activate_venv
    cd "$PROJECT_DIR"
    
    if [ ! -f "my_config.json" ]; then
        print_error "配置文件不存在，请先运行配置向导"
        exit 1
    fi
    
    print_message "启动交易机器人..."
    python src/main.py my_config.json
}

# 监控交易状态
monitor_trading() {
    print_header
    print_message "监控交易状态..."
    
    activate_venv
    cd "$PROJECT_DIR"
    
    print_message "检查进程状态..."
    ps aux | grep passivbot | grep -v grep || print_warning "未发现运行中的交易进程"
    
    print_message "检查日志..."
    if [ -f "logs/passivbot.log" ]; then
        tail -n 20 logs/passivbot.log
    else
        print_warning "日志文件不存在"
    fi
    
    print_message "检查账户余额..."
    python src/tools/fetch_balance.py --user $(grep -o '"user": "[^"]*"' my_config.json | cut -d'"' -f4) 2>/dev/null || print_warning "无法获取账户余额"
}

# 查看日志
view_logs() {
    print_header
    print_message "查看日志..."
    
    if [ -f "logs/passivbot.log" ]; then
        tail -f logs/passivbot.log
    else
        print_warning "日志文件不存在"
    fi
}

# 清理临时文件
clean_files() {
    print_header
    print_message "清理临时文件..."
    
    print_message "清理Python缓存..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_message "清理临时文件..."
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    print_message "清理完成"
}

# 主函数
main() {
    case "${1:-help}" in
        "help")
            show_help
            ;;
        "check")
            check_environment
            ;;
        "config")
            config_wizard
            ;;
        "backtest")
            run_backtest
            ;;
        "optimize")
            run_optimize
            ;;
        "trade")
            start_trading
            ;;
        "monitor")
            monitor_trading
            ;;
        "logs")
            view_logs
            ;;
        "clean")
            clean_files
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
