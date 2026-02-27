# 贡献指南

[English](CONTRIBUTING.md) | 简体中文

感谢您考虑为 Observational Memory 做出贡献！

## 如何贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 开发环境设置

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:3000 运行（开发模式）

### 后端开发

```bash
cargo run
```

后端将在 http://localhost:3000 运行

### 同时运行前后端

```bash
# 终端 1: 后端
cargo run

# 终端 2: 前端
cd frontend
npm run dev
```

## 测试

### 后端测试

```bash
# 运行所有测试
cargo test

# 运行特定测试
cargo test test_name

# 查看测试覆盖率
cargo test --coverage
```

### 前端测试

```bash
cd frontend
npm test
```

## 代码规范

### Rust 代码

- 遵循 Rust 官方代码规范
- 使用 `cargo fmt` 格式化代码
- 使用 `cargo clippy` 检查代码质量
- 添加适当的注释和文档

```bash
# 格式化代码
cargo fmt

# 检查代码
cargo clippy
```

### TypeScript/React 代码

- 使用 TypeScript 进行类型检查
- 遵循 ESLint 规则
- 使用函数式组件和 Hooks
- 添加适当的注释

```bash
# 检查代码
npm run lint

# 修复代码
npm run lint:fix
```

## 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/) 格式：

```
<类型>: <描述>

[可选的正文]

[可选的脚注]
```

### 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行的变动）
- `refactor`: 重构（既不是新增功能，也不是修改 bug 的代码变动）
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

### 示例

```bash
feat: 添加数据导出功能

添加了 JSON 格式的数据导出功能，用户可以导出所有会话数据。

Closes #123
```

## Pull Request 指南

### 提交前检查清单

- [ ] 代码已通过所有测试
- [ ] 代码已格式化（`cargo fmt` 和 `npm run lint`）
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有合并冲突

### PR 描述模板

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 重构

## 变更说明
简要描述您的更改...

## 相关 Issue
Closes #123

## 测试
描述您如何测试这些更改...

## 截图（如果适用）
添加截图以帮助解释您的更改...
```

## 问题反馈

### 报告 Bug

使用 [Bug 报告模板](https://github.com/kiss-kedaya/openclaw-observational-memory/issues/new?template=bug_report.md)

包含以下信息：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Rust 版本、Node.js 版本）
- 截图或日志

### 功能建议

使用 [功能请求模板](https://github.com/kiss-kedaya/openclaw-observational-memory/issues/new?template=feature_request.md)

包含以下信息：
- 功能描述
- 使用场景
- 预期效果
- 可选的实现方案

## 开发流程

### 1. 选择一个 Issue

- 查看 [Issues](https://github.com/kiss-kedaya/openclaw-observational-memory/issues)
- 选择一个标记为 `good first issue` 或 `help wanted` 的 Issue
- 在 Issue 中评论表明您想要处理它

### 2. 开发

- 创建新分支
- 编写代码
- 添加测试
- 更新文档

### 3. 提交

- 运行测试
- 格式化代码
- 提交更改
- 推送到您的 Fork

### 4. 创建 Pull Request

- 填写 PR 描述
- 等待代码审查
- 根据反馈进行修改

## 代码审查

所有提交都需要经过代码审查。审查者会检查：

- 代码质量
- 测试覆盖率
- 文档完整性
- 性能影响
- 安全性

## 社区准则

- 尊重他人
- 保持友好和专业
- 接受建设性批评
- 关注项目目标

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

## 联系方式

- GitHub Issues: [问题反馈](https://github.com/kiss-kedaya/openclaw-observational-memory/issues)
- GitHub Discussions: [讨论区](https://github.com/kiss-kedaya/openclaw-observational-memory/discussions)

## 致谢

感谢所有贡献者！

---

再次感谢您的贡献！ 🎉
