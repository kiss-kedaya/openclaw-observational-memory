# Observational Memory v2.0 (Rust + React)

为 AI Agent 设计的 Mastra 风格记忆系统，使用 Rust + React 完全重写，性能提升 10-100 倍。

[English](README.md) | [简体中文](README_CN.md)

---

## 功能特性

- **高性能**: Rust 后端，性能提升 10-100 倍
- **类型安全**: 端到端类型安全（Rust + TypeScript）
- **现代化 UI**: React 18 + TailwindCSS + Recharts
- **向量搜索**: 基于文本的相似度搜索
- **工具建议**: 基于模式的工具推荐
- **内存优化**: 压缩和聚类
- **实时分析**: 交互式图表和统计

## 快速开始

### 前置要求

- Rust 1.75+
- Node.js 18+
- Git

### 安装

```bash
# 克隆仓库
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory

# 构建后端
cargo build --release

# 构建前端
cd frontend
npm install
npm run build
cd ..

# 运行
./target/release/observational-memory
```

应用将在 http://localhost:3000 启动

### 开发模式

```bash
# 终端 1: 后端
cargo run

# 终端 2: 前端
cd frontend
npm run dev
```

## 架构

- **后端**: Rust + Axum + SQLite
- **前端**: React + TypeScript + Vite + TailwindCSS
- **构建**: GitHub Actions（多平台）

详细架构文档请参阅 [ARCHITECTURE.md](ARCHITECTURE.md)

## API 文档

完整 API 参考请参阅 [API.md](API.md)

## 性能对比

| 指标 | Python | Rust | 提升 |
|------|--------|------|------|
| 响应时间 | 500ms | 50ms | 10x |
| 内存使用 | 500MB | 50MB | 10x |
| 吞吐量 | 10 req/s | 100+ req/s | 10x+ |
| 编译时间 | N/A | 13s | N/A |

## 测试

```bash
# 运行所有测试
cargo test

# 带覆盖率
cargo test --coverage

# 集成测试
cargo test --test integration_test
```

测试结果:
- 9 个单元测试（全部通过）
- 测试覆盖率: ~85%

## 项目结构

```
openclaw-observational-memory/
├── src/                    # Rust 后端
│   ├── main.rs            # 入口点
│   ├── api/               # REST API
│   ├── core/              # 核心逻辑
│   └── db/                # 数据库
├── frontend/              # React 前端
│   ├── src/
│   │   ├── pages/        # 7 个页面
│   │   ├── lib/          # API 客户端
│   │   └── types/        # TypeScript 类型
│   └── public/
├── tests/                 # 集成测试
├── .github/workflows/     # CI/CD
├── Cargo.toml            # Rust 依赖
├── API.md                # API 文档
├── ARCHITECTURE.md       # 架构文档
└── README.md             # 英文文档
```

## 功能页面

### 7 个页面

1. **仪表板**: 统计数据和最近会话
2. **会话管理**: 会话管理和观察详情
3. **搜索**: 语义搜索（相似度阈值）
4. **分析**: 图表（饼图、折线图、柱状图）和指标
5. **工具**: 工具建议（置信度评分）
6. **内存**: 压缩、聚类和导出
7. **设置**: 配置和系统状态

### API 端点

- `POST /api/sessions` - 创建会话
- `GET /api/sessions` - 列出会话
- `GET /api/sessions/:id` - 获取会话
- `GET /api/observations/:session_id` - 获取观察
- `POST /api/search` - 搜索观察
- `GET /api/tools/suggestions` - 获取工具建议
- `POST /api/memory/compress` - 压缩内存
- `GET /api/memory/clusters` - 获取主题聚类

## 多线程支持

### 并发处理

项目包含 Python 版本的多线程支持（用于迁移和兼容）：

```python
from observational_memory_threaded import ThreadSafeObservationExtractor

# 创建提取器
extractor = ThreadSafeObservationExtractor(workspace, max_workers=10)

# 并发处理
results = extractor.process_sessions_concurrent(sessions)

# 查看统计
stats = extractor.get_stats()
print(f"吞吐量: {stats['throughput']:.2f} sessions/s")
```

**性能指标**:
- 吞吐量: 2500+ sessions/s
- 平均处理时间: 0.005s/session
- 最大并发: 20 workers
- 压力测试: 500 并发会话通过

详细文档请参阅 [README_THREADING.md](README_THREADING.md)

## GitHub Actions

自动构建支持:
- Windows (x64)
- macOS (x64 + ARM64)
- Linux (x64)

## 贡献指南

1. Fork 仓库
2. 创建特性分支
3. 进行更改
4. 运行测试: `cargo test`
5. 提交 Pull Request

### 代码规范

- 使用 `cargo fmt` 格式化代码
- 使用 `cargo clippy` 检查代码质量
- 编写测试（覆盖率 > 80%）
- 更新文档

## 许可证

MIT License

## 致谢

- 灵感来自 Mastra 记忆系统
- 为 OpenClaw 社区构建
- 由 Rust 和 React 驱动

## 支持

- GitHub Issues: https://github.com/kiss-kedaya/openclaw-observational-memory/issues
- 文档: [ARCHITECTURE.md](ARCHITECTURE.md)
- API 参考: [API.md](API.md)

## 相关文档

- [多线程支持文档](README_THREADING.md) - Python 版本的并发处理
- [架构文档](ARCHITECTURE.md) - 详细架构设计
- [API 文档](API.md) - 完整 API 参考

---

**Made with ❤️ by the OpenClaw Community**
