# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-27

### Added
- GitHub Actions 自动构建（5 个平台：Windows/macOS/Linux）
- 一键安装脚本（install.ps1）
- 全文搜索功能（search_full_text）
- 启动脚本（start_observational_memory.ps1）
- 详细使用文档（USAGE.md）
- 更新日志（CHANGELOG.md）

### Changed
- 搜索默认阈值：0.3 → 0.2（提高召回率）
- 优化搜索算法，提高关键词匹配准确度

### Fixed
- 数据库 UTF-8 编码设置（PRAGMA encoding）
- 中文显示问题（Windows 终端编码）
- API 响应头 Content-Type 设置

## [1.1.0] - 2026-02-27

### Added
- 高级搜索功能（多条件、正则、日期范围、优先级过滤）
- OpenClaw 集成（Hook + 自动启动 + 测试脚本）
- 数据库 schema 更新（tags, group_name, archived 字段）
- 后端 API（5 个新端点：tags/group/archive）
- 前端 API 客户端（5 个新方法）
- 会话管理增强（标签、分组、批量操作、归档 UI）
- 数据可视化增强（雷达图、热力图、图表导出 SVG）
- Memory 文件批量导入（25/26 文件成功）
- 导入脚本（import_memory.ps1, sync_memory.ps1）
- 文档（MEMORY_IMPORT.md）

### Changed
- Observer 改进（提取所有消息角色，不仅限 assistant）
- 数据库 SQL 语法修复（DEFAULT '[]' 而非 ''[]''）

### Fixed
- Hook 事件名称（message:received/sent）
- Hook Handler 格式（单一默认函数）
- API 500 错误（create_session 端点）
- 观察数据提取逻辑（当前 0 observations）
- message_count 和 token_count 更新（当前 0）
- API 消息保存功能（save_messages 调用）

## [1.0.0] - 2026-02-27

### Added
- Rust 后端（Axum 框架 + SQLite 数据库）
- Next.js 15 前端（App Router + TypeScript）
- 智能观察提取（Observer）
- 语义搜索（VectorSearchEngine）
- 工具建议（ToolSuggestionEngine）
- 内存优化（MemoryOptimizer）
- 数据可视化（5 种图表：饼图、雷达图、折线图、柱状图、热力图）
- 完全中文化（所有 UI 文本）
- 13 个 REST API 端点
- 7 个前端页面（会话、搜索、分析、设置等）
- 高级搜索功能
- 会话管理（标签、分组、归档）

### Technical Details
- 后端：Rust + Axum + SQLite + r2d2
- 前端：Next.js 15 + React + TypeScript + TailwindCSS + Recharts
- 性能目标：API < 50ms, 前端 < 1s, 内存 < 50MB
- 类型安全：端到端（Rust + TypeScript）

[1.2.0]: https://github.com/kiss-kedaya/openclaw-observational-memory/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/kiss-kedaya/openclaw-observational-memory/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/tag/v1.0.0
