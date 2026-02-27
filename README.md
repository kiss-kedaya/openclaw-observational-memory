# Observational Memory

> Mastra-inspired memory system that never forgets

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)](https://github.com/kiss-kedaya/openclaw-observational-memory)

[English](README.md) | [简体中文](README_CN.md)

## OpenClaw 自动集成

### 一键安装

```bash
python install_openclaw.py
openclaw gateway restart
```

完成！所有会话自动记录和观察。

详见 [OpenClaw Integration Guide](OPENCLAW_INTEGRATION.md)

---

## 快速开始

### 安装

```bash
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory
pip install -r requirements.txt
```

### 基础使用

```python
from observational_memory import ObservationalMemoryManager
from pathlib import Path

manager = ObservationalMemoryManager(Path.cwd())
result = manager.process_session(session_id, messages)
```

### Web UI

```bash
streamlit run app.py
```

访问 http://localhost:8501 查看 Web 界面。

---

## 功能特性

### 核心功能

- **Observer（观察者）**: 从对话中提取结构化观察
- **Reflector（反射器）**: 无损压缩观察数据
- **Priority System（优先级系统）**: 🔴 高 / 🟡 中 / 🟢 低
- **Temporal Anchoring（时间锚定）**: 双时间戳（说话时间 + 引用时间）

### 扩展功能

- **Multi-threading（多线程）**: 并发处理 10+ 会话
- **Vector Search（向量搜索）**: 语义相似度搜索
- **Web UI**: Streamlit 可视化界面
- **Data Management（数据管理）**: 导出/导入/备份
- **Plugin System（插件系统）**: 自定义提取器
- **i18n（国际化）**: 英文/中文双语支持

---

## 多线程支持

### 并发处理

```python
from observational_memory_concurrent import ConcurrentObservationalProcessor, ProcessingTask

processor = ConcurrentObservationalProcessor(Path.cwd(), max_workers=10)

tasks = [
    ProcessingTask(session_id, messages, priority=1)
    for session_id, messages in sessions.items()
]

results = processor.process_batch(tasks)
```

### 性能

- 单会话处理: < 1s
- 并发提速: 3-5x（5 workers）
- 线程安全: RLock 防死锁
- 优先级队列: 高优先级优先处理

---

## 向量搜索

### 语义搜索

```python
from observational_memory_vector import VectorSearchManager

vector_manager = VectorSearchManager(Path.cwd())

# 索引观察
vector_manager.index_observation(session_id, observation)

# 搜索
results = vector_manager.search("用户偏好", top_k=5, min_similarity=0.3)
```

### 特性

- 模型: sentence-transformers (all-MiniLM-L6-v2)
- 存储: SQLite + BLOB
- 性能: 索引 100 条 < 10s，搜索 < 1s
- 相似度: 余弦相似度

---

## Web UI

### 功能页面

1. **仪表板**: 统计数据、最近会话
2. **会话管理**: 浏览、搜索、删除
3. **语义搜索**: 向量搜索界面
4. **分析**: 优先级分布、时间线、Token 使用

### 特性

- 双语支持（中文/英文）
- Icon 导航（无 emoji）
- 动画效果（过渡、淡入、悬停）
- 响应式设计
- 暗色模式

### 启动

```bash
streamlit run app.py
```

---

## 数据管理

### 导出/导入

```bash
# 导出为 JSON
python data_manager.py export --session session_1 --format json

# 导出为 CSV
python data_manager.py export --session session_1 --format csv

# 导入
python data_manager.py import --input session_1.json
```

### 备份/恢复

```bash
# 创建备份
python data_manager.py backup --backup-name my_backup

# 恢复备份
python data_manager.py restore --input backups/my_backup.zip --overwrite

# 列出备份
python data_manager.py list-backups
```

---

## 插件系统

### 创建插件

```python
from plugin_system import ObservationPlugin

class MyPlugin(ObservationPlugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def extract(self, message: Dict[str, Any]) -> Optional[str]:
        # 自定义提取逻辑
        return "Extracted observation"
```

### 加载插件

```bash
# 列出插件
python plugin_system.py list

# 加载插件
python plugin_system.py load --plugin my_plugin
```

---

## API 文档

### ObservationalMemoryManager

```python
manager = ObservationalMemoryManager(workspace_dir: Path)

# 处理会话
result = manager.process_session(session_id: str, messages: List[Dict])

# 加载观察
observations = manager.load_observations(session_id: str)

# 保存观察
manager.save_observations(session_id: str, observations: str)
```

### ConcurrentObservationalProcessor

```python
processor = ConcurrentObservationalProcessor(
    workspace_dir: Path,
    max_workers: int = 10,
    progress_callback: Optional[Callable] = None
)

# 批量处理
results = processor.process_batch(tasks: List[ProcessingTask])

# 获取统计
stats = processor.get_statistics()
```

### VectorSearchManager

```python
manager = VectorSearchManager(
    workspace_dir: Path,
    model_name: str = "all-MiniLM-L6-v2"
)

# 索引
manager.index_observation(session_id: str, observation: str)

# 搜索
results = manager.search(
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.0
)
```

---

## 开发指南

### 项目结构

```
openclaw-observational-memory/
├── observational_memory.py          # 核心模块
├── observational_memory_concurrent.py  # 多线程
├── observational_memory_vector.py   # 向量搜索
├── data_manager.py                  # 数据管理
├── plugin_system.py                 # 插件系统
├── i18n.py                          # 国际化
├── app.py                           # Web UI
├── api/                             # FastAPI 后端
├── plugins/                         # 插件目录
├── locales/                         # 语言包
├── tests/                           # 测试文件
└── requirements.txt                 # 依赖
```

### 运行测试

```bash
# 所有测试
pytest

# 带覆盖率
pytest --cov=. --cov-report=term

# 特定模块
pytest test_concurrent.py -v
```

---

## 测试

### 测试覆盖率

| 模块 | 测试数 | 覆盖率 |
|------|--------|--------|
| observational_memory.py | 12 | 85% |
| observational_memory_concurrent.py | 13 | 76% |
| observational_memory_vector.py | 15 | 75% |
| data_manager.py | 8 | 90%+ |
| plugin_system.py | 4 | 85%+ |
| i18n.py | 4 | 90%+ |
| **总计** | **48** | **89%** |

---

## 性能

### 基准测试

| 操作 | 性能 |
|------|------|
| 单会话处理 | < 1s |
| 并发处理（10 会话，5 workers） | 3-5x 提速 |
| 向量索引（100 条，批量） | < 10s |
| 向量搜索（100 嵌入） | < 1s |
| Web UI 加载 | < 2s |
| 导出会话（JSON） | < 0.5s |
| 备份创建 | < 5s |

---

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 使用 Black 格式化代码
- 使用 Flake8 检查代码质量
- 编写测试（覆盖率 > 80%）
- 更新文档

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 致谢

- [Mastra](https://mastra.ai/) - 观察记忆架构灵感
- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent 框架
- [Sentence Transformers](https://www.sbert.net/) - 向量嵌入模型

---

## 链接

- [GitHub Repository](https://github.com/kiss-kedaya/openclaw-observational-memory)
- [Mastra Documentation](https://docs.mastra.ai/)
- [OpenClaw Documentation](https://docs.openclaw.ai/)

---

**Made with ❤️ by the OpenClaw Community**
