# Observational Memory for OpenClaw

> Mastra-inspired memory system that never forgets

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What is this?

Traditional AI agents "compact" (delete old messages) when they hit context limits, losing important information. **Observational Memory** solves this by extracting and compressing observations instead of discarding them.

Inspired by [Mastra Code](https://docs.mastra.ai/)'s observational memory architecture, this module extends [OpenClaw](https://github.com/openclaw/openclaw)'s Hermes Agent with:

- 🧠 **Observer**: Extract structured observations from conversations
- 🗜️ **Reflector**: Compress observations without losing information
- 🎯 **Priority System**: 🔴 High / 🟡 Medium / 🟢 Low
- ⏰ **Temporal Anchoring**: Dual timestamps (when said + when referenced)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from observational_memory import ObservationalMemoryManager
from pathlib import Path

# Initialize
manager = ObservationalMemoryManager(Path.cwd())

# Process a session
messages = [
    {"role": "user", "content": "帮我安装 agent-browser", "timestamp": "2026-02-27T09:00:00"},
    {"role": "assistant", "content": "好的，我来安装", "timestamp": "2026-02-27T09:00:10"},
    {"role": "assistant", "content": "安装成功！", "timestamp": "2026-02-27T09:01:00"}
]

result = manager.process_session("session_123", messages)
print(result['observations'])
```

**Output:**
```markdown
Date: 2026-02-27
* 🔴 (09:00) User stated: 帮我安装 agent-browser
* 🟡 (09:01) Agent completed: 安装成功！
```

## 📚 Features

### 1. Observer - Extract Observations

The Observer extracts key information from conversations:

- **User Facts**: "我是开发者" → 🔴 High priority
- **Preferences**: "我喜欢用 Python" → 🔴 High priority
- **Completed Tasks**: "安装成功" → 🟡 Medium priority
- **Tool Usage**: "执行了 npm install" → 🟡 Medium priority

### 2. Reflector - Compress Observations

When observations exceed 30k tokens, the Reflector compresses them:

1. Keep all 🔴 high-priority observations
2. Merge similar 🟡 medium-priority observations
3. Remove 🟢 low-priority observations
4. Deduplicate by content hash

### 3. Priority System

- 🔴 **High**: User facts, preferences, goals, critical context
- 🟡 **Medium**: Project details, tool results, technical operations
- 🟢 **Low**: Minor details, uncertain observations

### 4. Temporal Anchoring

Each observation has dual timestamps:

```markdown
* 🔴 (09:15) User will visit parents this weekend. (meaning June 17-18, 2026)
       ↑                                                    ↑
   When said                                      When referenced
```

## 🔧 Integration with OpenClaw

### Unified Monitor Service

The module integrates seamlessly with OpenClaw's unified monitor:

```python
# In unified_monitor.py
from observational_memory import ObservationalMemoryManager

obs_manager = ObservationalMemoryManager(Path.cwd())

# In session check loop
if len(messages) > 10:
    result = obs_manager.process_session(session_id, messages)
    if result['token_count'] > 30000:
        print(f"Generated observations: {result['compressed_token_count']} tokens")
```

### Context Injection

Inject observations into agent context:

```python
context = manager.get_context_for_session(session_id)
# Returns formatted context with observations
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Conversation                         │
│  User: "帮我安装 agent-browser"                         │
│  Agent: "好的，我来安装"                                │
│  Agent: "安装成功！"                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                     Observer                            │
│  Extracts structured observations                       │
│  - User stated: 帮我安装 agent-browser (🔴)            │
│  - Agent completed: 安装成功 (🟡)                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    Reflector                            │
│  Compresses when > 30k tokens                           │
│  - Keeps all 🔴 high priority                           │
│  - Merges similar 🟡 medium priority                    │
│  - Removes 🟢 low priority                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 Observations File                       │
│  memory/observations/session_123.md                     │
└─────────────────────────────────────────────────────────┘
```

## 🎓 Comparison with Mastra

| Feature | Mastra | This Implementation | Status |
|---------|--------|---------------------|--------|
| Observer | ✅ | ✅ | Complete |
| Reflector | ✅ | ✅ | Complete |
| Priority System | ✅ | ✅ | Complete |
| Temporal Anchoring | ✅ | ✅ | Complete |
| Auto Compression | ✅ | ✅ | Complete |
| Context Injection | ✅ | 🟡 | Partial |
| Multi-thread | ✅ | ❌ | Future |

## 📖 Documentation

- [Core Algorithm Research](./mastra-observational-memory-research.md) - Deep dive into Mastra's architecture
- [Integration Plan](./mastra-integration-plan.md) - How we integrated it
- [API Reference](./docs/API.md) - Complete API documentation

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [Mastra](https://mastra.ai/) - For the original observational memory architecture
- [OpenClaw](https://github.com/openclaw/openclaw) - For the amazing AI agent framework
- [Hermes Agent](https://github.com/hermes-agent) - For the memory system inspiration

## 🔗 Links

- [Mastra Code Documentation](https://docs.mastra.ai/)
- [OpenClaw Documentation](https://docs.openclaw.ai/)
- [GitHub Repository](https://github.com/kiss-kedaya/openclaw-observational-memory)

---

**Made with ❤️ by the OpenClaw Community**
