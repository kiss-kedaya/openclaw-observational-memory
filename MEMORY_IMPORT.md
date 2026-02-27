# Memory 导入指南

## 批量导入历史文件

导入所有 Memory 文件到 Observational Memory：

```powershell
.\import_memory.ps1
```

**结果**：
- 成功导入 25 个文件
- 失败 1 个文件（openclaw-releases-full.md，文件过大）

## 增量同步

同步今日日志和 MEMORY.md：

```powershell
.\sync_memory.ps1
```

**同步内容**：
- 今日日志（YYYY-MM-DD.md）
- 全局记忆（MEMORY.md）

## 自动同步

### 方法 1：Cron Job（推荐）

添加到 `openclaw.json`：

```json
{
  "cron": {
    "memory-sync": {
      "schedule": "0 * * * *",
      "command": "powershell -ExecutionPolicy Bypass -File F:\\GO\\openclaw-observational-memory\\sync_memory.ps1",
      "enabled": true
    }
  }
}
```

### 方法 2：Windows 计划任务

```powershell
# 创建每小时同步任务
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File F:\GO\openclaw-observational-memory\sync_memory.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "ObservationalMemorySync" -Action $action -Trigger $trigger
```

## 导入的会话

所有导入的会话使用以下命名规则：

- 日志文件：`memory-YYYY-MM-DD`
- 特殊文件：`memory-<filename>`
- 今日日志：`daily-log-YYYY-MM-DD`
- 全局记忆：`global-memory`

## 查看导入结果

1. 打开 http://localhost:3000
2. 点击 "会话管理"
3. 搜索 "memory-" 查看所有导入的会话

## 故障排除

### 导入失败

如果某些文件导入失败：

1. 检查文件大小（过大的文件可能超时）
2. 检查文件编码（必须是 UTF-8）
3. 检查 API 服务是否运行

### 同步失败

如果同步失败：

1. 确保 Observational Memory 服务运行中
2. 检查文件路径是否正确
3. 查看错误日志

## 手动重新导入

如果需要重新导入某个文件：

```powershell
$file = "C:\Users\34438\.openclaw\workspace\memory\2026-02-27.md"
$content = Get-Content $file -Raw -Encoding UTF8
$body = @{
    session_id = "memory-2026-02-27"
    messages = @(@{
        role = "system"
        content = $content
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    })
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Post -Body $body -ContentType "application/json"
```
