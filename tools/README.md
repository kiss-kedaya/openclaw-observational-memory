# README: Polling 模式使用说明

## 概述

Polling 模式是 Hook 模式的备用方案，直接读取 OpenClaw 会话文件并同步到 Observational Memory。

## 优势

1. **不依赖 Hook** - 直接读取会话文件
2. **100% 捕获率** - 所有会话都会被同步
3. **历史数据** - 可以导入所有历史会话
4. **稳定可靠** - 不受 OpenClaw 事件系统影响

## 使用方法

### 手动启动

```powershell
cd tools
.\start_poller.ps1
```

### 自动启动

在 `start_observational_memory.ps1` 中添加：

```powershell
# 启动 Polling 服务
Start-Process powershell -ArgumentList "-NoExit", "-File", "tools\start_poller.ps1" -WindowStyle Minimized
```

## 配置

编辑 `tools/session_poller.py`:

- `OPENCLAW_SESSIONS_DIR`: OpenClaw 会话文件目录
- `MEMORY_API`: Observational Memory API 地址
- `POLL_INTERVAL`: 轮询间隔（秒）

## 工作原理

1. 每 60 秒扫描 OpenClaw 会话文件
2. 解析 JSONL 格式的会话记录
3. 提取消息内容（user/assistant/system）
4. 同步到 Observational Memory API
5. 记录已处理的文件（避免重复）

## 依赖

- Python 3.8+
- requests

安装依赖：

```bash
uv pip install requests
```
