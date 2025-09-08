#!/bin/bash

# Passivbot 快速启动脚本
# 适用于 OpenCloudOS 9.4 + Python 3.11.6 + Rust 1.89.0
# 使用方法: ./quick_start.sh [命令]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目路径（自动检测）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_DIR/venv"
RUST_ENV="$HOME/.cargo/env"

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
    echo -e "${BLUE}  环境: OpenCloudOS 9.4${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 检查环境
check_environment() {
    print_header
    print_message "检查环境..."
    
    # 检查项目目录
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    
    # 检查虚拟环境
    if [ ! -d "$VENV_PATH" ]; then
        print_error "虚拟环境不存在，请先运行部署脚本"
        print_message "运行: python3 -m venv venv"
        exit 1
    fi
    
    # 检查Python版本
    if [ -f "$VENV_PATH/bin/python" ]; then
        PYTHON_VERSION=$("$VENV_PATH/bin/python" --version 2>&1)
        print_message "Python版本: $PYTHON_VERSION"
    else
        print_error "虚拟环境中Python不存在"
        exit 1
    fi
    
    # 检查Rust环境
    if [ -f "$RUST_ENV" ]; then
        source "$RUST_ENV" 2>/dev/null || true
        if command -v rustc >/dev/null 2>&1; then
            RUST_VERSION=$(rustc --version 2>&1)
            print_message "Rust版本: $RUST_VERSION"
        else
            print_warning "Rust未安装或未在PATH中"
        fi
    else
        print_warning "Rust环境文件不存在"
    fi
    
    # 检查核心依赖
    print_message "检查核心依赖..."
    source "$VENV_PATH/bin/activate"
    
    # 检查关键Python包
    local missing_packages=()
    for package in passivbot_rust ccxt pandas numpy hjson matplotlib; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -eq 0 ]; then
        print_success "所有核心依赖已安装"
    else
        print_warning "缺少依赖包: ${missing_packages[*]}"
        print_message "运行: pip install ${missing_packages[*]}"
    fi
    
    # 检查配置文件
    if [ ! -f "$PROJECT_DIR/api-keys.json" ]; then
        print_warning "API密钥文件不存在"
        print_message "运行: cp api-keys.json.example api-keys.json"
    else
        print_success "API密钥文件存在"
    fi
    
    if [ ! -f "$PROJECT_DIR/my_config.json" ]; then
        print_warning "配置文件不存在"
        print_message "运行: cp configs/template.json my_config.json"
    else
        print_success "配置文件存在"
    fi
    
    print_success "环境检查完成"
}

# 激活环境
activate_environment() {
    print_message "激活环境..."
    
    # 激活虚拟环境
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        print_message "虚拟环境已激活"
    else
        print_error "虚拟环境激活文件不存在"
        exit 1
    fi
    
    # 激活Rust环境
    if [ -f "$RUST_ENV" ]; then
        source "$RUST_ENV" 2>/dev/null || true
        print_message "Rust环境已激活"
    fi
    
    # 切换到项目目录
    cd "$PROJECT_DIR"
    print_message "已切换到项目目录: $PROJECT_DIR"
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
    echo "  demo         运行离线回测演示"
    echo "  backtest     运行完整回测"
    echo "  optimize     运行参数优化"
    echo "  trade        启动实盘交易"
    echo "  tmux         在tmux中启动交易"
    echo "  monitor      监控交易状态"
    echo "  logs         查看日志"
    echo "  balance      查看账户余额"
    echo "  clean        清理临时文件"
    echo "  update       更新依赖包"
    echo "  rebuild      重新构建Rust扩展"
    echo "  web          启动Web配置服务器"
    echo "  web-enhanced 启动增强版Web服务器"
    echo "  config-manage 配置管理工具"
    echo ""
    echo "示例:"
    echo "  $0 check     # 检查环境"
    echo "  $0 demo      # 运行离线演示"
    echo "  $0 backtest  # 运行回测"
    echo "  $0 tmux      # 在tmux中启动交易"
    echo "  $0 web-enhanced # 启动增强版Web服务"
    echo "  $0 config-manage # 配置管理工具"
    echo ""
    echo "系统信息:"
    echo "  操作系统: OpenCloudOS 9.4"
    echo "  Python: 3.11.6 (虚拟环境)"
    echo "  Rust: 1.89.0"
    echo "  项目路径: $PROJECT_DIR"
}

# 配置向导
config_wizard() {
    print_header
    print_message "配置向导"
    
    # 检查API密钥
    if [ ! -f "$PROJECT_DIR/api-keys.json" ]; then
        print_message "创建API密钥文件..."
        if [ -f "$PROJECT_DIR/api-keys.json.example" ]; then
            cp "$PROJECT_DIR/api-keys.json.example" "$PROJECT_DIR/api-keys.json"
            print_success "API密钥文件已创建"
            print_warning "请编辑 api-keys.json 文件，添加您的API密钥"
        else
            print_error "API密钥模板文件不存在"
            exit 1
        fi
    else
        print_success "API密钥文件已存在"
    fi
    
    # 检查配置文件
    if [ ! -f "$PROJECT_DIR/my_config.json" ]; then
        print_message "创建配置文件..."
        if [ -f "$PROJECT_DIR/configs/template.json" ]; then
            cp "$PROJECT_DIR/configs/template.json" "$PROJECT_DIR/my_config.json"
            print_success "配置文件已创建"
            print_warning "请编辑 my_config.json 文件，配置交易参数"
        else
            print_error "配置模板文件不存在"
            exit 1
        fi
    else
        print_success "配置文件已存在"
    fi
    
    # 创建日志目录
    if [ ! -d "$PROJECT_DIR/logs" ]; then
        mkdir -p "$PROJECT_DIR/logs"
        print_success "日志目录已创建"
    fi
    
    print_success "配置完成！"
    print_message "下一步: 编辑配置文件，然后运行回测"
    print_message "配置文件位置:"
    print_message "  API密钥: $PROJECT_DIR/api-keys.json"
    print_message "  交易配置: $PROJECT_DIR/my_config.json"
}

# 运行离线回测演示
run_demo() {
    print_header
    print_message "运行离线回测演示..."
    
    activate_environment
    
    if [ ! -f "offline_backtest_demo.py" ]; then
        print_error "离线回测演示文件不存在"
        exit 1
    fi
    
    print_message "开始离线回测演示..."
    python offline_backtest_demo.py
    
    print_success "离线回测演示完成！"
    print_message "查看结果: cat backtest_result.json"
}

# 运行完整回测
run_backtest() {
    print_header
    print_message "运行完整回测..."
    
    activate_environment
    
    # 确定配置文件
    local config_file="${1:-my_config.json}"
    if [[ ! -f "$config_file" ]]; then
        print_error "配置文件不存在: $config_file"
        exit 1
    fi
    print_success "配置文件存在"
    print_message "配置文件来源: 本地文件"
    
    # 检查网络连接
    print_message "检查网络连接..."
    if ! ping -c 1 api.binance.com >/dev/null 2>&1; then
        print_warning "网络连接可能有问题，建议先运行离线演示"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message "已取消"
            exit 0
        fi
    fi
    
    print_message "开始回测..."
    print_warning "回测过程可能需要较长时间，请耐心等待..."
    
    # 设置回测参数
    local start_date="${2:-2024-01-01}"
    local end_date="${3:-2024-06-01}"
    
    python src/backtest.py "$config_file"
    
    print_success "回测完成！"
    
    # 自动显示盈利结果
    show_profit_results
}

# 检查配置文件
check_config_file() {
    if [ ! -f "my_config.json" ]; then
        print_warning "默认配置文件不存在"
        if [ -f "web_config/my_config.json" ]; then
            print_message "发现网页服务保存的配置文件"
            print_message "配置文件来源: 网页服务"
            print_message "是否使用网页服务保存的配置？(y/N): "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cp "web_config/my_config.json" "my_config.json"
                print_success "已使用网页服务保存的配置"
            else
                print_error "请先运行配置向导或使用网页服务保存配置"
                exit 1
            fi
        else
            print_error "配置文件不存在，请先运行配置向导或使用网页服务保存配置"
            print_message "建议使用: ./quick_start.sh web-enhanced"
            exit 1
        fi
    else
        print_success "配置文件存在"
        # 检查配置文件来源
        if [ -f "web_config/my_config.json" ]; then
            if [ "my_config.json" -nt "web_config/my_config.json" ]; then
                print_message "配置文件来源: 本地文件 (比网页服务配置更新)"
            else
                print_message "配置文件来源: 网页服务"
            fi
        else
            print_message "配置文件来源: 本地文件"
        fi
    fi
}

# 显示盈利结果
show_profit_results() {
    print_message "分析回测盈利结果..."
    
    # 找到最新的回测结果目录
    local backtest_dir="backtests/combined"
    if [ ! -d "$backtest_dir" ]; then
        print_error "未找到回测结果目录"
        return 1
    fi
    
    # 获取最新的回测结果目录
    local latest_dir=$(ls -t "$backtest_dir" | head -1)
    local result_path="$backtest_dir/$latest_dir"
    
    echo
    echo -e "\033[1;36m🎯 回测盈利结果\033[0m"
    echo -e "\033[1;36m==========================================\033[0m"
    echo -e "\033[0;32m📅 回测时间:\033[0m $latest_dir"
    echo -e "\033[0;32m📁 结果目录:\033[0m $result_path"
    echo
    
    # 检查分析文件是否存在
    if [ -f "$result_path/analysis.json" ]; then
        # 使用Python快速解析JSON并显示关键指标
        python3 -c "
import json
import sys

try:
    with open('$result_path/analysis.json', 'r') as f:
        data = json.load(f)
    
    # 计算关键指标
    initial_balance = 10000
    final_balance = initial_balance * (1 + data.get('gain', 0))
    total_profit = final_balance - initial_balance
    total_return = data.get('gain', 0)
    
    print('\033[0;33m💰 核心盈利指标\033[0m')
    print('\033[0;33m------------------------------\033[0m')
    print(f'初始资金:     \${initial_balance:,.2f}')
    print(f'最终资金:     \${final_balance:,.2f}')
    print(f'总收益:       \${total_profit:,.2f}')
    print(f'总收益率:     {total_return*100:.2f}%')
    print()
    
    print('\033[0;33m📊 风险指标\033[0m')
    print('\033[0;33m------------------------------\033[0m')
    print(f'最大回撤:     {data.get(\"drawdown_worst\", 0)*100:.2f}%')
    print(f'夏普比率:     {data.get(\"sharpe_ratio\", 0):.4f}')
    print(f'索提诺比率:   {data.get(\"sortino_ratio\", 0):.4f}')
    print()
    
    print('\033[0;33m📈 交易统计\033[0m')
    print('\033[0;33m------------------------------\033[0m')
    print(f'日均持仓数:   {data.get(\"positions_held_per_day\", 0):.1f}')
    print(f'平均持仓时间: {data.get(\"position_held_hours_mean\", 0):.2f} 小时')
    print()
    
    # 读取交易记录
    import pandas as pd
    try:
        df = pd.read_csv('$result_path/fills.csv')
        total_trades = len(df)
        profitable_trades = len(df[df['pnl'] > 0])
        total_pnl = df['pnl'].sum()
        total_fees = df['fee_paid'].sum()
        
        print('\033[0;33m💼 交易记录\033[0m')
        print('\033[0;33m------------------------------\033[0m')
        print(f'总交易次数:   {total_trades}')
        print(f'盈利交易:     {profitable_trades}')
        print(f'胜率:         {profitable_trades/total_trades*100:.1f}%' if total_trades > 0 else '胜率:         0.0%')
        print(f'总交易盈亏:   \${total_pnl:.2f}')
        print(f'总手续费:     \${total_fees:.2f}')
        print(f'净收益:       \${total_pnl - total_fees:.2f}')
        print()
        
        # 显示最大盈利和亏损
        if not df.empty:
            max_profit = df['pnl'].max()
            max_loss = df['pnl'].min()
            print('\033[0;33m🏆 单笔交易极值\033[0m')
            print('\033[0;33m------------------------------\033[0m')
            print(f'最大单笔盈利: \${max_profit:.2f}')
            print(f'最大单笔亏损: \${max_loss:.2f}')
            print()
            
    except Exception as e:
        print(f'无法读取交易记录: {e}')
    
    print('\033[1;36m==========================================\033[0m')
    print('\033[0;32m✅ 盈利分析完成！\033[0m')
    print(f'\033[0;32m📊 详细数据: $result_path\033[0m')
    
except Exception as e:
    print(f'分析失败: {e}')
    sys.exit(1)
"
    else
        print_error "未找到分析结果文件"
        return 1
    fi
    
    echo
    print_message "查看详细结果: ls -la $result_path"
    print_message "查看图表: ls -la $result_path/*.png"
}

# 运行参数优化
run_optimize() {
    print_header
    print_message "运行参数优化..."
    
    activate_environment
    
    # 检查配置文件
    check_config_file
    
    print_warning "优化过程可能需要很长时间..."
    print_warning "建议在tmux会话中运行以避免中断"
    
    read -p "确认开始优化？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_message "已取消"
        exit 0
    fi
    
    # 设置优化参数
    local iters="${2:-100}"
    local population="${3:-20}"
    
    print_message "开始优化 (迭代次数: $iters, 种群大小: $population)..."
    python src/optimize.py my_config.json \
        --optimize.iters "$iters" \
        --optimize.population_size "$population"
    
    print_success "优化完成！"
    print_message "查看结果: ls -la backtests/*/optimize/"
}

# 启动实盘交易
start_trading() {
    print_header
    print_warning "启动实盘交易..."
    print_warning "请确保您已经充分测试并了解风险！"
    print_warning "建议先在测试网或小资金上测试！"
    
    read -p "确认启动实盘交易？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_message "已取消"
        exit 0
    fi
    
    activate_environment
    
    # 确定配置文件
    local config_file="${1:-my_config.json}"
    if [[ ! -f "$config_file" ]]; then
        print_error "配置文件不存在: $config_file"
        exit 1
    fi
    print_success "配置文件存在: $config_file"
    
    # 显示配置摘要
    echo
    print_message "配置摘要:"
    if command -v jq >/dev/null 2>&1; then
        echo "  用户: $(jq -r '.live.user // "未设置"' "$config_file" 2>/dev/null)"
        echo "  币种: $(jq -r '.live.approved_coins.long[0] // "未设置"' "$config_file" 2>/dev/null)"
        echo "  杠杆: $(jq -r '.live.leverage // "未设置"' "$config_file" 2>/dev/null)"
        echo "  币种数量: $(jq -r '.live.approved_coins.long | length' "$config_file" 2>/dev/null)"
    else
        echo "  配置文件: $config_file"
        echo "  注意: 需要安装jq来显示详细配置"
    fi
    
    # 检查API密钥配置
    if ! grep -q '"key": "key"' api-keys.json; then
        print_warning "请确保API密钥已正确配置"
    fi
    
    print_message "启动交易机器人..."
    python src/main.py "$config_file"
}

# 在tmux中启动交易
start_tmux_trading() {
    print_header
    print_message "在tmux中启动交易..."
    
    # 检查tmux是否安装
    if ! command -v tmux >/dev/null 2>&1; then
        print_error "tmux未安装，请先安装tmux"
        print_message "运行: yum install -y tmux"
        exit 1
    fi
    
    # 检查是否已有passivbot会话
    if tmux has-session -t passivbot 2>/dev/null; then
        print_warning "passivbot会话已存在"
        read -p "是否连接到现有会话？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            tmux attach-session -t passivbot
            exit 0
        fi
    fi
    
    print_message "创建新的tmux会话..."
    tmux new-session -d -s passivbot -c "$PROJECT_DIR" \
        "source venv/bin/activate && source ~/.cargo/env && python src/main.py my_config.json"
    
    print_success "交易已在tmux会话中启动"
    print_message "连接到会话: tmux attach-session -t passivbot"
    print_message "分离会话: Ctrl+b 然后按 d"
    print_message "查看会话: tmux list-sessions"
}

# 监控交易状态
monitor_trading() {
    print_header
    print_message "监控交易状态..."
    
    # 检查tmux会话
    if tmux has-session -t passivbot 2>/dev/null; then
        print_success "发现passivbot tmux会话"
        tmux list-sessions | grep passivbot
    else
        print_warning "未发现passivbot tmux会话"
    fi
    
    # 检查进程
    print_message "检查进程状态..."
    if pgrep -f "python.*main.py" >/dev/null; then
        print_success "发现运行中的交易进程"
        ps aux | grep "python.*main.py" | grep -v grep
    else
        print_warning "未发现运行中的交易进程"
    fi
    
    # 检查日志
    print_message "检查日志..."
    if [ -f "logs/passivbot.log" ]; then
        print_success "日志文件存在"
        echo "最近的日志:"
        tail -n 10 logs/passivbot.log
    else
        print_warning "日志文件不存在"
    fi
    
    # 检查配置文件
    if [ -f "my_config.json" ]; then
        print_message "当前配置的用户:"
        grep -o '"user": "[^"]*"' my_config.json | cut -d'"' -f4 || print_warning "未找到用户配置"
    fi
}

# 查看日志
view_logs() {
    print_header
    print_message "查看日志..."
    
    if [ -f "logs/passivbot.log" ]; then
        print_message "实时查看日志 (按Ctrl+C退出)..."
        tail -f logs/passivbot.log
    else
        print_warning "日志文件不存在"
        print_message "日志文件位置: logs/passivbot.log"
    fi
}

# 查看账户余额
check_balance() {
    print_header
    print_message "查看账户余额..."
    
    activate_environment
    
    if [ ! -f "my_config.json" ]; then
        print_error "配置文件不存在"
        exit 1
    fi
    
    # 提取用户配置
    local user=$(grep -o '"user": "[^"]*"' my_config.json | cut -d'"' -f4)
    if [ -z "$user" ]; then
        print_error "未找到用户配置"
        exit 1
    fi
    
    print_message "查询用户: $user"
    
    if [ -f "src/tools/fetch_balance.py" ]; then
        python src/tools/fetch_balance.py --user "$user"
    else
        print_warning "余额查询工具不存在"
    fi
}

# 清理临时文件
clean_files() {
    print_header
    print_message "清理临时文件..."
    
    print_message "清理Python缓存..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    print_message "清理临时文件..."
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    print_message "清理回测缓存..."
    find . -name "*.npy" -mtime +30 -delete 2>/dev/null || true
    
    print_success "清理完成"
}

# 启动Web配置服务器
start_web_server() {
    print_header
    print_message "启动Web配置服务器..."
    
    web_config_dir="$PROJECT_DIR/web_config"
    if [ ! -d "$web_config_dir" ]; then
        print_error "Web配置目录不存在: $web_config_dir"
        exit 1
    fi
    
    cd "$web_config_dir"
    
    if [ -f "start_server.py" ]; then
        print_message "启动基础版Web服务器..."
        python3 start_server.py
    else
        print_error "Web服务器文件不存在"
        exit 1
    fi
}

# 启动增强版Web服务器
start_enhanced_web_server() {
    print_header
    print_message "启动增强版Web服务器..."
    
    web_config_dir="$PROJECT_DIR/web_config"
    if [ ! -d "$web_config_dir" ]; then
        print_error "Web配置目录不存在: $web_config_dir"
        exit 1
    fi
    
    cd "$web_config_dir"
    
    if [ -f "start_enhanced.py" ]; then
        print_message "启动增强版Web服务器..."
        print_message "功能包括:"
        print_message "  ✅ 配置保存到服务器"
        print_message "  ✅ 在线执行回测"
        print_message "  ✅ 实时查看回测结果"
        print_message "  ✅ 自动盈利分析"
        python3 start_enhanced.py
    else
        print_error "增强版Web服务器文件不存在"
        exit 1
    fi
}

# 配置管理
manage_config() {
    print_header
    print_message "配置管理工具"
    
    while true; do
        echo
        print_message "请选择操作:"
        echo "  1) 查看当前配置状态"
        echo "  2) 使用网页服务配置"
        echo "  3) 备份当前配置"
        echo "  4) 恢复配置"
        echo "  5) 比较配置文件"
        echo "  6) 启动网页配置服务"
        echo "  0) 退出"
        echo
        read -p "请输入选择 (0-6): " choice
        
        case $choice in
            1)
                show_config_status
                ;;
            2)
                use_web_config
                ;;
            3)
                backup_config
                ;;
            4)
                restore_config
                ;;
            5)
                compare_configs
                ;;
            6)
                start_enhanced_web_server
                ;;
            0)
                print_message "退出配置管理"
                break
                ;;
            *)
                print_error "无效选择，请重新输入"
                ;;
        esac
    done
}

# 显示配置状态
show_config_status() {
    print_header
    print_message "配置文件状态"
    
    echo
    print_message "本地配置文件:"
    if [ -f "my_config.json" ]; then
        print_success "✅ my_config.json 存在"
        echo "  修改时间: $(stat -c %y my_config.json 2>/dev/null || echo '未知')"
        echo "  文件大小: $(stat -c %s my_config.json 2>/dev/null || echo '未知') 字节"
        
        # 显示配置摘要
        if command -v jq >/dev/null 2>&1; then
            echo "  用户: $(jq -r '.live.user // "未设置"' my_config.json 2>/dev/null)"
            echo "  交易所: $(jq -r '.backtest.exchanges[0] // "未设置"' my_config.json 2>/dev/null)"
            echo "  初始资金: $(jq -r '.backtest.starting_balance // "未设置"' my_config.json 2>/dev/null)"
        fi
    else
        print_warning "❌ my_config.json 不存在"
    fi
    
    echo
    print_message "网页服务配置:"
    if [ -f "web_config/my_config.json" ]; then
        print_success "✅ web_config/my_config.json 存在"
        echo "  修改时间: $(stat -c %y web_config/my_config.json 2>/dev/null || echo '未知')"
        echo "  文件大小: $(stat -c %s web_config/my_config.json 2>/dev/null || echo '未知') 字节"
        
        # 显示配置摘要
        if command -v jq >/dev/null 2>&1; then
            echo "  用户: $(jq -r '.live.user // "未设置"' web_config/my_config.json 2>/dev/null)"
            echo "  交易所: $(jq -r '.backtest.exchanges[0] // "未设置"' web_config/my_config.json 2>/dev/null)"
            echo "  初始资金: $(jq -r '.backtest.starting_balance // "未设置"' web_config/my_config.json 2>/dev/null)"
        fi
    else
        print_warning "❌ web_config/my_config.json 不存在"
    fi
    
    echo
    print_message "配置备份:"
    backup_count=$(ls -1 config_backup_*.json 2>/dev/null | wc -l)
    if [ $backup_count -gt 0 ]; then
        print_success "✅ 发现 $backup_count 个配置备份"
        ls -la config_backup_*.json 2>/dev/null | head -5
    else
        print_warning "❌ 没有配置备份"
    fi
}

# 使用网页服务配置
use_web_config() {
    print_header
    print_message "使用网页服务配置"
    
    if [ ! -f "web_config/my_config.json" ]; then
        print_error "网页服务配置文件不存在"
        print_message "请先启动网页服务并保存配置"
        return 1
    fi
    
    # 备份当前配置
    if [ -f "my_config.json" ]; then
        backup_file="config_backup_$(date +%Y%m%d_%H%M%S).json"
        cp "my_config.json" "$backup_file"
        print_success "已备份当前配置到: $backup_file"
    fi
    
    # 复制网页服务配置
    cp "web_config/my_config.json" "my_config.json"
    print_success "已使用网页服务配置"
    
    # 显示配置摘要
    if command -v jq >/dev/null 2>&1; then
        echo
        print_message "配置摘要:"
        echo "  用户: $(jq -r '.live.user // "未设置"' my_config.json)"
        echo "  交易所: $(jq -r '.backtest.exchanges[0] // "未设置"' my_config.json)"
        echo "  初始资金: $(jq -r '.backtest.starting_balance // "未设置"' my_config.json)"
    fi
}

# 备份配置
backup_config() {
    print_header
    print_message "备份配置文件"
    
    if [ ! -f "my_config.json" ]; then
        print_error "没有配置文件可备份"
        return 1
    fi
    
    backup_file="config_backup_$(date +%Y%m%d_%H%M%S).json"
    cp "my_config.json" "$backup_file"
    print_success "配置已备份到: $backup_file"
}

# 恢复配置
restore_config() {
    print_header
    print_message "恢复配置文件"
    
    # 列出可用的备份文件
    backup_files=($(ls -1 config_backup_*.json 2>/dev/null | sort -r))
    
    if [ ${#backup_files[@]} -eq 0 ]; then
        print_error "没有找到配置备份文件"
        return 1
    fi
    
    echo
    print_message "可用的配置备份:"
    for i in "${!backup_files[@]}"; do
        echo "  $((i+1))) ${backup_files[$i]}"
        echo "     修改时间: $(stat -c %y "${backup_files[$i]}" 2>/dev/null || echo '未知')"
    done
    
    echo
    read -p "请选择要恢复的备份 (1-${#backup_files[@]}): " choice
    
    if [[ $choice =~ ^[0-9]+$ ]] && [ $choice -ge 1 ] && [ $choice -le ${#backup_files[@]} ]; then
        selected_file="${backup_files[$((choice-1))]}"
        
        # 备份当前配置
        if [ -f "my_config.json" ]; then
            current_backup="config_backup_$(date +%Y%m%d_%H%M%S).json"
            cp "my_config.json" "$current_backup"
            print_success "已备份当前配置到: $current_backup"
        fi
        
        # 恢复选中的配置
        cp "$selected_file" "my_config.json"
        print_success "已恢复配置: $selected_file"
    else
        print_error "无效选择"
    fi
}

# 比较配置文件
compare_configs() {
    print_header
    print_message "比较配置文件"
    
    if [ ! -f "my_config.json" ] && [ ! -f "web_config/my_config.json" ]; then
        print_error "没有配置文件可比较"
        return 1
    fi
    
    if [ -f "my_config.json" ] && [ -f "web_config/my_config.json" ]; then
        print_message "比较本地配置和网页服务配置:"
        echo
        if command -v diff >/dev/null 2>&1; then
            if diff -q "my_config.json" "web_config/my_config.json" >/dev/null; then
                print_success "配置文件相同"
            else
                print_warning "配置文件不同"
                echo
                print_message "差异详情:"
                diff -u "my_config.json" "web_config/my_config.json" | head -20
            fi
        else
            print_warning "diff命令不可用，无法比较文件"
        fi
    elif [ -f "my_config.json" ]; then
        print_message "只有本地配置文件存在"
    elif [ -f "web_config/my_config.json" ]; then
        print_message "只有网页服务配置文件存在"
    fi
}

# 更新依赖包
update_dependencies() {
    print_header
    print_message "更新依赖包..."
    
    activate_environment
    
    print_message "更新pip..."
    pip install --upgrade pip
    
    print_message "更新Python包..."
    pip install --upgrade -r requirements.txt
    
    print_success "依赖包更新完成"
}

# 重新构建Rust扩展
rebuild_rust() {
    print_header
    print_message "重新构建Rust扩展..."
    
    activate_environment
    
    if [ ! -d "passivbot-rust" ]; then
        print_error "Rust扩展目录不存在"
        exit 1
    fi
    
    print_message "进入Rust目录..."
    cd passivbot-rust
    
    print_message "清理之前的构建..."
    cargo clean 2>/dev/null || true
    
    print_message "重新构建Rust扩展..."
    maturin develop --release
    
    print_message "返回项目目录..."
    cd ..
    
    print_success "Rust扩展重新构建完成"
    
    # 测试导入
    print_message "测试Rust扩展..."
    if python -c "import passivbot_rust; print('Rust扩展导入成功')"; then
        print_success "Rust扩展工作正常"
    else
        print_error "Rust扩展导入失败"
        exit 1
    fi
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
        "demo")
            run_demo
            ;;
        "backtest")
            shift  # 移除 "backtest" 参数
            run_backtest "$@"
            ;;
        "optimize")
            run_optimize "$@"
            ;;
        "trade")
            shift  # 移除 "trade" 参数
            start_trading "$@"
            ;;
        "tmux")
            start_tmux_trading
            ;;
        "monitor")
            monitor_trading
            ;;
        "logs")
            view_logs
            ;;
        "balance")
            check_balance
            ;;
        "clean")
            clean_files
            ;;
        "update")
            update_dependencies
            ;;
        "rebuild")
            rebuild_rust
            ;;
        "web")
            start_web_server
            ;;
        "web-enhanced")
            start_enhanced_web_server
            ;;
        "config-manage")
            manage_config
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