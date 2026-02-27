# 观察记忆系统 (Observational Memory)

[English](README.md) | 简体中文

AI Agent 记忆管理系统 - 自动提取、压缩和检索对话中的观察记录

## ✨ 特性

- 🧠 **智能观察提取** - 自动从对话中提取关键信息
- 🔍 **语义搜索** - 基于向量的相似度搜索
- 📊 **数据可视化** - 优先级分布、时间线、Token 使用统计
- 🔄 **实时更新** - 自动刷新会话数据
- 💾 **数据管理** - 导入/导出功能
- 🌐 **完全中文化** - 所有 UI 均为中文
- ⚡ **高性能** - Rust 后端，10-100x 性能提升

## 🚀 快速开始

### 前置要求

- Rust 1.75+
- Node.js 20+
- npm 或 yarn

### 安装

1. 克隆仓库
```bash
git clone https://github.com/kiss-kedaya/openclaw-observational-memory.git
cd openclaw-observational-memory
```

2. 构建前端
```bash
cd frontend
npm install
npm run build
```

3. 构建后端
```bash
cd ..
cargo build --release
```

4. 运行
```bash
./target/release/observational-memory
```

5. 打开浏览器访问 http://localhost:3000

## 📖 功能说明

### 仪表盘
- 总会话数、总观察数、总 Token 数统计
- 最近会话列表

### 会话管理
- 创建新会话
- 查看会话详情
- 查看观察记录
- 优先级标签（高/中/低）

### 搜索
- 关键词搜索
- 相似度阈值调整
- 搜索结果展示

### 数据分析
- 优先级分布饼图
- 会话时间线折线图
- Token 使用柱状图

### 工具建议
- 工具使用建议列表
- 工具统计

### 记忆管理
- 压缩记忆
- 查看聚类
- 高级搜索

### 设置
- API 地址配置
- 数据导入/导出
- 系统状态

## 🏗️ 技术栈

### 前端
- Next.js 15 (App Router)
- React 18
- TypeScript
- TailwindCSS
- Recharts (图表)
- Axios (HTTP 客户端)

### 后端
- Rust
- Axum (Web 框架)
- SQLite (数据库)
- Tokio (异步运行时)

## 📊 性能

- API 响应时间: < 50ms
- 内存占用: < 50MB
- 并发支持: > 100 req/s
- 性能提升: 10-100x (相比 Python 版本)

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING_CN.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [GitHub 仓库](https://github.com/kiss-kedaya/openclaw-observational-memory)
- [问题反馈](https://github.com/kiss-kedaya/openclaw-observational-memory/issues)
- [Python 版本](https://github.com/kiss-kedaya/openclaw-observational-memory/tree/python-legacy)
- [API 文档](API_CN.md)
- [项目路线图](ROADMAP_CN.md)
- [更新日志](CHANGELOG_CN.md)

## 📝 更新日志

查看 [CHANGELOG_CN.md](CHANGELOG_CN.md) 了解版本更新历史。
