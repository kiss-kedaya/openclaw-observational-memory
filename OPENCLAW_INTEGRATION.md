# OpenClaw Integration Guide

## 自动集成

Observational Memory 可以自动集成到 OpenClaw，无需手动配置。

## 快速安装

```bash
# 1. 克隆项目
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory

# 2. 运行安装脚本
python install_openclaw.py

# 3. 重启 OpenClaw Gateway
openclaw gateway restart
```

完成！所有会话将自动记录和观察。

---

## 工作原理

### 自动处理流程

1. **消息监听**: Hook 监听所有会话消息
2. **阈值检查**: 当会话超过 10 条消息时触发
3. **自动处理**: 提取观察并索引到向量数据库
4. **自动备份**: 可选，每 24 小时自动备份

### 集成方式

**方式 1: Gateway Hook（已实现）**
- 文件: `~/.openclaw/hooks/observational_memory_hook.py`
- 自动加载，无需修改 OpenClaw 代码
- 支持所有 Agent 和会话

**方式 2: Unified Monitor（可选）**
- 集成到 `tools/unified_monitor.py`
- 定期扫描会话
- 适合批量处理

**方式 3: Agent 级别（可选）**
- 在 Agent 配置中添加
- 仅处理特定 Agent 的会话

---

## 配置

### 配置文件

位置: `~/.openclaw/hooks/observational_memory_config.json`

```json
{
  "min_messages": 10,
  "auto_index": true,
  "auto_backup": false,
  "backup_interval_hours": 24,
  "workspace_dir": "~/.openclaw/workspace",
  "enabled": true,
  "log_level": "INFO"
}
```

### 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `min_messages` | 触发处理的最小消息数 | 10 |
| `auto_index` | 自动索引到向量数据库 | true |
| `auto_backup` | 自动备份 | false |
| `backup_interval_hours` | 备份间隔（小时） | 24 |
| `workspace_dir` | 工作目录 | ~/.openclaw/workspace |
| `enabled` | 启用/禁用 | true |
| `log_level` | 日志级别 | INFO |

---

## 使用

### 查看观察

```bash
# 启动 Web UI
observational-memory start

# 或在浏览器访问
http://localhost:8501
```

### 搜索观察

```bash
# CLI 搜索
observational-memory search "用户偏好"

# Python API
from observational_memory import ObservationalMemory
om = ObservationalMemory()
results = om.search("用户偏好", top_k=5)
```

### 导出数据

```bash
# 导出会话
observational-memory export session_123 --format json

# 创建备份
observational-memory backup --name my_backup
```

---

## 高级用法

### 手动处理会话

```python
from observational_memory import ObservationalMemory

om = ObservationalMemory()

# 处理特定会话
messages = [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
]

result = om.process_session("session_id", messages)
```

### 自定义 Hook

```python
# ~/.openclaw/hooks/custom_hook.py
from observational_memory import ObservationalMemory

om = ObservationalMemory()

def on_message_complete(session_id, messages):
    # 自定义逻辑
    if "重要" in messages[-1]["content"]:
        om.process_session(session_id, messages)
```

### 批量处理历史会话

```python
from observational_memory import ObservationalMemory
from pathlib import Path
import json

om = ObservationalMemory()

# 处理所有历史会话
sessions_dir = Path("~/.openclaw/workspace/sessions").expanduser()
for session_file in sessions_dir.glob("*.json"):
    session_data = json.loads(session_file.read_text())
    om.process_session(session_data["id"], session_data["messages"])
```

---

## 故障排除

### Hook 未生效

1. 检查文件是否存在:
   ```bash
   ls ~/.openclaw/hooks/observational_memory_hook.py
   ```

2. 检查配置:
   ```bash
   cat ~/.openclaw/hooks/observational_memory_config.json
   ```

3. 重启 Gateway:
   ```bash
   openclaw gateway restart
   ```

### 观察未生成

1. 检查消息数是否达到阈值（默认 10 条）
2. 查看日志: `~/.openclaw/logs/gateway.log`
3. 手动测试:
   ```python
   from integrations.openclaw_hook import on_message_complete
   on_message_complete("test", [{"role": "user", "content": "test"}] * 11)
   ```

### 向量搜索不工作

1. 检查是否安装依赖:
   ```bash
   pip list | grep sentence-transformers
   ```

2. 重新索引:
   ```python
   from observational_memory import ObservationalMemory
   om = ObservationalMemory()
   # 重新处理会话会自动索引
   ```

---

## 卸载

```bash
# 1. 删除 Hook
rm ~/.openclaw/hooks/observational_memory_hook.py
rm ~/.openclaw/hooks/observational_memory_config.json

# 2. 卸载包
pip uninstall observational-memory

# 3. 重启 Gateway
openclaw gateway restart
```

---

## 性能优化

### 减少处理频率

```json
{
  "min_messages": 20
}
```

### 禁用自动索引

```json
{
  "auto_index": false
}
```

### 批量处理

使用 Unified Monitor 定期批量处理，而非实时处理。

---

## 安全性

### 数据隐私

- 所有数据存储在本地
- 不发送到外部服务器
- 向量嵌入在本地生成

### 访问控制

- Web UI 默认仅本地访问（localhost）
- 可配置密码保护（Streamlit 配置）

---

## 更新

```bash
cd openclaw-observational-memory
git pull
python install_openclaw.py
```

---

## 支持

- GitHub Issues: https://github.com/kiss-kedaya/openclaw-observational-memory/issues
- Documentation: https://github.com/kiss-kedaya/openclaw-observational-memory

---

**Made with ❤️ for OpenClaw Community**
