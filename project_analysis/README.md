# Passivbot 项目分析文档

本文件夹包含对 Passivbot 项目的详细分析文档。

## 文档结构

- `功能分析.md` - 详细的功能分析报告
- `技术架构.md` - 技术架构和代码结构分析
- `项目概览.md` - 项目整体概览和总结

## 分析日期

分析日期：2024年12月

## 项目版本

当前分析基于 Passivbot v7.3.20

---

*这些文档基于对项目源代码、配置文件和文档的详细分析生成。*

## 快速开始

### 1. 使用快速启动脚本
```bash
# 查看帮助
./quick_start.sh help

# 检查环境
./quick_start.sh check

# 配置向导
./quick_start.sh config

# 运行回测
./quick_start.sh backtest

# 启动交易
./quick_start.sh trade
```

### 2. 手动运行步骤
1. 激活虚拟环境: `source venv/bin/activate`
2. 配置API密钥: 编辑 `api-keys.json`
3. 创建配置文件: 复制 `my_config_template.json` 为 `my_config.json`
4. 运行回测: `python src/backtest.py my_config.json`
5. 启动交易: `python src/main.py my_config.json`

### 3. 详细运行流程
请参考 `运行流程指南.md` 获取完整的操作指南。


## 交易策略分析

### 策略文档
- `交易策略分析.md` - 详细的策略原理和参数分析
- `策略流程图.md` - 策略执行流程和架构图

### 核心策略特点
1. **反向做市策略** - 不预测价格，提供流动性
2. **网格交易系统** - 在预设价格点自动买卖
3. **追踪订单系统** - 动态跟随价格移动
4. **解套机制** - 智能管理卡住仓位
5. **风险管理系统** - 多层级风险控制

### 策略参数
- **多头网格间距**: 2.7%
- **空头网格间距**: 3.7%
- **钱包风险限制**: 200%
- **解套阈值**: 68%


## 自定义策略开发

### 策略插件系统
Passivbot现在支持自定义策略插件系统，允许你实现自己的交易策略而无需修改核心代码。

### 快速开始
```bash
# 测试策略插件系统
python test_strategy.py

# 使用自定义策略配置
python src/main.py my_ma_crossover_config.json
```

### 策略开发文档
- `自定义策略开发指南.md` - 完整的策略开发指南
- `src/strategies/` - 策略插件系统源码
- `my_ma_crossover_config.json` - MA交叉策略配置示例

### 已实现的策略
1. **默认策略** - 原有的网格+追踪策略
2. **MA交叉策略** - 移动平均线交叉策略示例

### 策略特点
- **插拔式设计** - 无需修改核心代码
- **配置驱动** - 通过JSON配置文件控制
- **完整回调** - 支持市场数据、仓位、订单回调
- **日志记录** - 详细的策略执行日志
- **参数验证** - 自动验证订单格式


## 回测功能

### 回测方式
1. **完整回测** - 使用官方回测系统（需要网络连接）
2. **离线回测** - 使用模拟数据（无需网络连接）

### 快速开始
```bash
# 离线回测演示
python offline_backtest_demo.py

# 完整回测（需要网络）
python src/backtest.py config.json --disable_plotting
```

### 回测工具
- `offline_backtest_demo.py` - 离线回测演示脚本
- `simple_backtest_demo.py` - 数据准备脚本
- `src/backtest.py` - 官方回测系统
- `src/optimize.py` - 参数优化工具

### 回测结果
- 收益率分析
- 交易统计
- 风险指标
- 可视化图表

### 回测文档
- `回测使用指南.md` - 完整的回测使用指南

