# Observational Memory 使用指南

## 快速开始

### 方式 1：使用预编译版本（推荐）

1. 下载最新版本：
   - Windows: [observational-memory-windows-x64.exe](https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest)
   - macOS (Intel): [observational-memory-macos-x64](https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest)
   - macOS (Apple Silicon): [observational-memory-macos-arm64](https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest)
   - Linux: [observational-memory-linux-x64](https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest)

2. 运行程序：
   ```bash
   # Windows
   .\observational-memory.exe
   
   # macOS/Linux
   chmod +x observational-memory-*
   ./observational-memory-*
   ```

3. 访问 http://localhost:3000

### 方式 2：一键安装（Windows）

```powershell
# 下载并运行安装脚本
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kiss-kedaya/openclaw-observational-memory/master/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### 方式 3：从源码编译

参见 [README.md](README.md)

## OpenClaw 集成

### 自动记录对话

1. 安装 Hook：
   ```bash
   openclaw hooks install F:/GO/openclaw-observational-memory/hook
   ```

2. 启用 Hook：
   ```bash
   openclaw hooks enable observational-memory
   ```

3. 重启 Gateway：
   ```bash
   openclaw gateway restart
   ```

### 验证 Hook

```bash
openclaw hooks list
# 应该看到：🧠 observational-memory ✓ Ready
```

## Agent 使用

### 在 AGENTS.md 中添加

参见 [README_CN.md](README_CN.md#agent-集成)

### 使用 API

```powershell
# 搜索历史对话
$body = @{
    query = "Wails 配置"
    threshold = 0.2
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:3000/api/search" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## API 使用

### 搜索对话

```powershell
$body = @{
    query = "搜索关键词"
    threshold = 0.2
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:3000/api/search" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### 获取会话列表

```powershell
$sessions = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get
```

### 获取观察记录

```powershell
$observations = Invoke-RestMethod -Uri "http://localhost:3000/api/observations/session-id" -Method Get
```

## 常见问题

### Q: 中文显示乱码？

A: 这是 Windows 终端编码问题，不影响实际功能。Web UI (http://localhost:3000) 显示正常。

### Q: 搜索没有结果？

A: 
1. 检查数据库中是否有数据
2. 降低搜索阈值（threshold）
3. 使用更通用的关键词

### Q: Hook 没有记录对话？

A:
1. 检查 Hook 是否启用：`openclaw hooks list`
2. 检查服务是否运行：`Test-NetConnection localhost -Port 3000`
3. 重启 Gateway：`openclaw gateway restart`

### Q: 如何备份数据？

A: 复制 `memory.db` 文件即可

## 高级功能

### Polling 模式

如果 Hook 不稳定，可以使用 Polling 模式：

```powershell
cd tools
.\start_poller.ps1
```

### 批量导入历史数据

```powershell
.\import_memory.ps1
```

## 性能优化

- 数据库大小：建议定期清理旧数据
- 搜索性能：调整 threshold 参数
- 内存使用：Rust 后端内存占用 < 50MB

## 更新日志

参见 [CHANGELOG.md](CHANGELOG.md)
