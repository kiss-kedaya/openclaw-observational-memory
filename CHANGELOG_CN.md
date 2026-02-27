# 更新日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.1] - 2026-02-27

### 新增
- ✨ Next.js 15 前端（App Router）
- ✨ 完全中文化 UI（所有页面和组件）
- ✨ 数据可视化（饼图、折线图、柱状图）
- ✨ 数据导入/导出功能
- ✨ 自动刷新功能（每 30 秒）
- ✨ GitHub Actions 多平台构建（Windows/macOS/Linux）
- ✨ 7 个完整功能页面
- ✨ 统一的 API 客户端

### 改进
- 🎨 优化 UI 过渡效果
- 🎨 改善按钮悬停效果
- 🎨 统一禁用状态样式
- ⚡ 统一 API 调用方式（axios）
- ⚡ 性能提升 10-100x（相比 Python 版本）
- 📱 响应式设计

### 修复
- 🐛 修复 GitHub Actions 权限问题（添加 contents: write）
- 🐛 修复 API 客户端问题（统一使用 axios）
- 🐛 修复前端 TypeScript 配置（添加 jsx: react-jsx）
- 🐛 修复 .gitignore 导致 api.ts 无法提交的问题

### 技术栈
- **前端**: Next.js 15, React 18, TypeScript, TailwindCSS, Recharts
- **后端**: Rust, Axum, SQLite, Tokio
- **构建**: GitHub Actions, 多平台支持

## [1.0.0] - 2026-02-26

### 新增
- 🎉 初始版本发布
- ✨ Rust 后端完整实现
- ✨ Python 版本（已移至 python-legacy 分支）
- ✨ 4 个开发阶段完成
- ✨ OpenClaw 集成
- ✨ 工具建议引擎
- ✨ 记忆优化器
- ✨ 向量搜索引擎
- ✨ 8 个 REST API 端点

### 功能
- 会话管理
- 观察记录提取
- 语义搜索
- 工具建议
- 记忆压缩
- 主题聚类

### 性能
- API 响应 < 50ms
- 内存占用 < 50MB
- 并发支持 > 100 req/s

## [0.9.0] - 2026-02-18 (Python 版本)

### 新增
- Python 后端实现
- Streamlit UI
- 基础向量搜索
- 工具建议
- 记忆优化

### 已弃用
- Python 版本已弃用，推荐使用 Rust 版本
- Python 代码已移至 python-legacy 分支

---

[1.0.1]: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/tag/v1.0.1
[1.0.0]: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/tag/v1.0.0
[0.9.0]: https://github.com/kiss-kedaya/openclaw-observational-memory/tree/python-legacy
