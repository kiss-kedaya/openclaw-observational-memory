# Observational Memory for OpenClaw

> 受 Mastra 启发的永不遗忘的记忆系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 这是什么？

传统的 AI Agent 在达到上下文限制时会"压缩"（删除旧消息），导致重要信息丢失。**Observational Memory** 通过提取和压缩观察而非丢弃消息来解决这个问题。

受 [Mastra Code](https://docs.mastra.ai/) 的观察记忆架构启发，本模块为 [OpenClaw](https://github.com/openclaw/openclaw) 的 Hermes Agent 扩展了以下功能：

- 🧠 **Observer（观察者）**：从对话中提取结构化观察
- 🗜️ **Reflector（反思者）**：压缩观察而不丢失信息
- 🎯 **优先级系统**：🔴 高 / 🟡 中 / 🟢 低
- ⏰ **时间锚定**：双时间戳（说的时间 + 引用的时间）

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory

# 安装依赖
pip install -r requirements.txt
```

### 基础使用

```python
from observational_memory import ObservationalMemoryManager
from pathlib import Path

# 初始化
manager = ObservationalMemoryManager(Path.cwd())

# 处理会话
messages = [
    {"role": "user", "content": "帮我安装 agent-browser", "timestamp": "2026-02-27T09:00:00"},
    {"role": "assistant", "content": "好的，我来安装", "timestamp": "2026-02-27T09:00:10"},
    {"role": "assistant", "content": "安装成功！", "timestamp": "2026-02-27T09:01:00"}
]

result = manager.process_session("session_123", messages)
print(result['observations'])
```

**输出：**
```markdown
Date: 2026-02-27
* 🔴 (09:00) User stated: 帮我安装 agent-browser
* 🟡 (09:01) Agent completed: 安装成功！
```

## 📚 核心功能

### 1. Observer - 提取观察

Observer 从对话中提取关键信息：

- **用户事实**："我是开发者" → 🔴 高优先级
- **用户偏好**："我喜欢用 Python" → 🔴 高优先级
- **已完成任务**："安装成功" → 🟡 中优先级
- **工具使用**："执行了 npm install" → 🟡 中优先级

### 2. Reflector - 压缩观察

当观察超过 30k tokens 时，Reflector 会压缩它们：

1. 保留所有 🔴 高优先级观察
2. 合并相似的 🟡 中优先级观察
3. 移除 🟢 低优先级观察
4. 通过内容哈希去重

### 3. 优先级系统

- 🔴 **高优先级**：用户事实、偏好、目标、关键上下文
- 🟡 **中优先级**：项目细节、工具结果、技术操作
- 🟢 **低优先级**：次要细节、不确定的观察

### 4. 时间锚定

每个观察都有双时间戳：

```markdown
* 🔴 (09:15) User will visit parents this weekend. (meaning June 17-18, 2026)
       ↑                                                    ↑
   说的时间                                          引用的时间
```

## 🔧 与 OpenClaw 集成

### 统一监控服务

本模块与 OpenClaw 的统一监控服务无缝集成：

```python
# 在 unified_monitor.py 中
from observational_memory import ObservationalMemoryManager

obs_manager = ObservationalMemoryManager(Path.cwd())

# 在会话检查循环中
if len(messages) > 10:
    result = obs_manager.process_session(session_id, messages)
    if result['token_count'] > 30000:
        print(f"生成观察: {result['compressed_token_count']} tokens")
```

### 上下文注入

将观察注入到 Agent 上下文：

```python
context = manager.get_context_for_session(session_id)
# 返回格式化的上下文和观察
```

## 📊 架构

```
┌─────────────────────────────────────────────────────────┐
│                    对话                                  │
│  用户: "帮我安装 agent-browser"                         │
│  Agent: "好的，我来安装"                                │
│  Agent: "安装成功！"                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  Observer（观察者）                      │
│  提取结构化观察                                          │
│  - User stated: 帮我安装 agent-browser (🔴)            │
│  - Agent completed: 安装成功 (🟡)                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Reflector（反思者）                      │
│  当超过 30k tokens 时压缩                                │
│  - 保留所有 🔴 高优先级                                  │
│  - 合并相似的 🟡 中优先级                                │
│  - 移除 🟢 低优先级                                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 观察文件                                 │
│  memory/observations/session_123.md                     │
└─────────────────────────────────────────────────────────┘
```

## 🎓 与 Mastra 的对比

| 功能 | Mastra | 本实现 | 状态 |
|------|--------|--------|------|
| Observer | ✅ | ✅ | 完成 |
| Reflector | ✅ | ✅ | 完成 |
| 优先级系统 | ✅ | ✅ | 完成 |
| 时间锚定 | ✅ | ✅ | 完成 |
| 自动压缩 | ✅ | ✅ | 完成 |
| 上下文注入 | ✅ | 🟡 | 部分完成 |
| 多线程 | ✅ | ❌ | 未来计划 |

## 📖 文档

- [核心算法研究](./mastra-observational-memory-research.md) - 深入了解 Mastra 的架构
- [集成计划](./mastra-integration-plan.md) - 我们如何集成它
- [API 参考](./docs/API.md) - 完整的 API 文档

## 🧪 测试

运行测试：

```bash
pytest test_observational_memory.py -v
```

测试覆盖：

```bash
pytest test_observational_memory.py --cov=observational_memory
```

**测试结果**：
- ✅ 12 个单元测试
- ✅ 100% 测试通过
- ✅ 覆盖所有核心功能

## 🤝 贡献

欢迎贡献！请先阅读我们的[贡献指南](./CONTRIBUTING.md)。

### 开发设置

```bash
# 克隆仓库
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory

# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# 运行测试
pytest -v

# 代码格式化
black observational_memory.py test_observational_memory.py

# 代码检查
flake8 observational_memory.py
mypy observational_memory.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件。

## 🙏 致谢

- [Mastra](https://mastra.ai/) - 原始的观察记忆架构
- [OpenClaw](https://github.com/openclaw/openclaw) - 强大的 AI Agent 框架
- [Hermes Agent](https://github.com/hermes-agent) - 记忆系统灵感

## 🔗 相关链接

- [Mastra Code 文档](https://docs.mastra.ai/)
- [OpenClaw 文档](https://docs.openclaw.ai/)
- [GitHub 仓库](https://github.com/kiss-kedaya/openclaw-observational-memory)
- [问题反馈](https://github.com/kiss-kedaya/openclaw-observational-memory/issues)

## 💡 使用场景

### 1. 长期对话记忆

```python
# 会话 1
manager.process_session("user_123", [
    {"role": "user", "content": "我喜欢用 Python 编程"}
])

# 会话 2（几天后）
context = manager.get_context_for_session("user_123")
# Agent 会记住用户喜欢 Python
```

### 2. 项目上下文保持

```python
# 记录项目决策
manager.process_session("project_abc", [
    {"role": "user", "content": "我们决定使用 PostgreSQL"},
    {"role": "assistant", "content": "好的，已记录"}
])

# 后续对话会记住这个决策
```

### 3. 技能学习

```python
# Agent 学习解决问题的方法
manager.process_session("learning", [
    {"role": "user", "content": "agent-browser daemon 启动失败"},
    {"role": "assistant", "content": "需要手动启动 daemon"}
])

# 下次遇到类似问题会记住解决方案
```

## 🎯 核心优势

### vs 传统压缩

| 传统方式 | Observational Memory |
|---------|---------------------|
| ❌ 删除旧消息 | ✅ 提取观察 |
| ❌ 丢失信息 | ✅ 保留精华 |
| ❌ 无优先级 | ✅ 智能优先级 |
| ❌ 无时间感知 | ✅ 时间锚定 |

### 为什么不压缩？

传统 Agent 的"压缩"是**丢弃旧消息**，我们的"压缩"是**提取精华**：

- ❌ 传统：删除旧消息 → 丢失信息
- ✅ 我们：提取观察 → 保留关键信息

### 三层记忆结构

- **短期**：最近未观察的消息（原始对话）
- **中期**：观察（提取的关键信息）
- **长期**：反思后的观察（压缩但不丢失）

## 🚧 未来计划

- [ ] 多线程支持
- [ ] 向量搜索集成
- [ ] 更智能的观察提取（使用 LLM）
- [ ] Web UI 界面
- [ ] 观察可视化
- [ ] 导出/导入功能
- [ ] 多语言支持

## 📞 联系方式

- GitHub Issues: [提交问题](https://github.com/kiss-kedaya/openclaw-observational-memory/issues)
- Telegram: [@kedaya_798](https://t.me/kedaya_798)

---

**由 OpenClaw 社区用 ❤️ 制作**
