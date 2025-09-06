# Passivbot 快速启动指南

## 🚀 快速开始

### 1. 检查环境
```bash
./quick_start.sh check
```
这会检查：
- Python 3.11.6 虚拟环境
- Rust 1.89.0 环境
- 所有核心依赖包
- 配置文件状态

### 2. 配置向导
```bash
./quick_start.sh config
```
这会：
- 创建 `api-keys.json` 文件
- 创建 `my_config.json` 配置文件
- 创建日志目录

### 3. 运行离线演示
```bash
./quick_start.sh demo
```
无需网络连接，使用模拟数据测试策略。

## 📋 完整命令列表

### 基础命令
- `./quick_start.sh help` - 显示帮助信息
- `./quick_start.sh check` - 检查环境和依赖
- `./quick_start.sh config` - 配置向导

### 回测和优化
- `./quick_start.sh demo` - 运行离线回测演示
- `./quick_start.sh backtest` - 运行完整回测
- `./quick_start.sh optimize` - 运行参数优化

### 交易管理
- `./quick_start.sh trade` - 启动实盘交易
- `./quick_start.sh tmux` - 在tmux中启动交易
- `./quick_start.sh monitor` - 监控交易状态
- `./quick_start.sh balance` - 查看账户余额

### 维护命令
- `./quick_start.sh logs` - 查看日志
- `./quick_start.sh clean` - 清理临时文件
- `./quick_start.sh update` - 更新依赖包
- `./quick_start.sh rebuild` - 重新构建Rust扩展

## 🔧 详细使用说明

### 环境检查
```bash
./quick_start.sh check
```
输出示例：
```
================================
  Passivbot 快速启动脚本
  环境: OpenCloudOS 9.4
================================
[INFO] 检查环境...
[INFO] Python版本: Python 3.11.6
[INFO] Rust版本: rustc 1.89.0
[SUCCESS] 所有核心依赖已安装
[SUCCESS] API密钥文件存在
[SUCCESS] 配置文件存在
[SUCCESS] 环境检查完成
```

### 配置向导
```bash
./quick_start.sh config
```
这会创建必要的配置文件：
- `api-keys.json` - API密钥配置
- `my_config.json` - 交易参数配置
- `logs/` - 日志目录

### 离线回测演示
```bash
./quick_start.sh demo
```
特点：
- 无需网络连接
- 使用模拟数据
- 快速验证策略
- 生成回测报告

### 完整回测
```bash
./quick_start.sh backtest
```
或者指定时间范围：
```bash
./quick_start.sh backtest 2024-01-01 2024-06-01
```

### 参数优化
```bash
./quick_start.sh optimize
```
或者指定参数：
```bash
./quick_start.sh optimize 500 50  # 500次迭代，种群大小50
```

### tmux交易管理
```bash
# 启动tmux交易会话
./quick_start.sh tmux

# 连接到现有会话
tmux attach-session -t passivbot

# 分离会话（在tmux内按 Ctrl+b 然后按 d）
# 查看所有会话
tmux list-sessions
```

### 监控和日志
```bash
# 监控交易状态
./quick_start.sh monitor

# 实时查看日志
./quick_start.sh logs

# 查看账户余额
./quick_start.sh balance
```

## ⚙️ 配置文件说明

### API密钥配置 (api-keys.json)
```json
{
    "binance_01": {
        "exchange": "binance",
        "key": "your_api_key",
        "secret": "your_secret"
    }
}
```

### 交易配置 (my_config.json)
主要配置项：
- `live.user` - 对应api-keys.json中的账户名
- `live.approved_coins` - 允许交易的币种
- `bot.long` - 多头策略参数
- `bot.short` - 空头策略参数

## 🛠️ 故障排除

### 环境问题
```bash
# 重新检查环境
./quick_start.sh check

# 更新依赖
./quick_start.sh update

# 重新构建Rust扩展
./quick_start.sh rebuild
```

### 配置文件问题
```bash
# 重新运行配置向导
./quick_start.sh config

# 检查配置文件语法
python -c "import hjson; hjson.load(open('my_config.json'))"
```

### 交易问题
```bash
# 检查tmux会话
tmux list-sessions

# 查看日志
./quick_start.sh logs

# 监控状态
./quick_start.sh monitor
```

## 📊 使用流程建议

### 新手流程
1. `./quick_start.sh check` - 检查环境
2. `./quick_start.sh config` - 配置向导
3. `./quick_start.sh demo` - 运行演示
4. 编辑配置文件
5. `./quick_start.sh backtest` - 回测验证
6. `./quick_start.sh optimize` - 参数优化
7. `./quick_start.sh tmux` - 启动交易

### 日常使用
1. `./quick_start.sh monitor` - 检查状态
2. `./quick_start.sh logs` - 查看日志
3. `./quick_start.sh balance` - 查看余额

### 维护流程
1. `./quick_start.sh clean` - 清理文件
2. `./quick_start.sh update` - 更新依赖
3. `./quick_start.sh rebuild` - 重建扩展

## ⚠️ 重要提醒

1. **风险提示**: 加密货币交易存在高风险
2. **测试优先**: 建议先运行演示和回测
3. **小资金开始**: 实盘交易建议小资金测试
4. **定期监控**: 使用tmux和监控命令
5. **备份配置**: 定期备份重要配置文件

## 📞 技术支持

- 查看项目文档: `docs/` 文件夹
- 查看项目分析: `project_analysis/` 文件夹
- 查看部署总结: `DEPLOYMENT_SUMMARY.md`

---

**脚本版本**: 适配 OpenCloudOS 9.4  
**Python版本**: 3.11.6  
**Rust版本**: 1.89.0  
**更新时间**: 2025年9月6日