# OpenClaw 集成指南

## 快速开始

### 1. 自动启动 Observational Memory

```powershell
.\start_observational_memory.ps1
```

### 2. 访问 Web UI

打开浏览器访问: http://localhost:3000

或使用桌面快捷方式

### 3. OpenClaw 自动集成

Hook 已安装到: `C:\Users\34438\.openclaw\hooks\observational_memory.py`

所有对话会自动记录到 Observational Memory。

## 功能

- ✅ 自动记录所有对话
- ✅ 会话管理
- ✅ 观察记录
- ✅ 高级搜索
- ✅ 数据分析
- ✅ 工具建议
- ✅ 记忆管理

## 测试集成

```powershell
.\test_integration.ps1
```

## 手动配置 OpenClaw Gateway

如果需要手动配置，编辑 `C:\Users\34438\.openclaw\openclaw.json`:

```json
{
  "hooks": {
    "observational_memory": {
      "enabled": true,
      "path": "hooks/observational_memory.py",
      "events": ["message", "session_end"]
    }
  }
}
```

## 故障排除

### 服务未启动

```powershell
# 检查进程
Get-Process -Name "observational-memory"

# 重新启动
.\start_observational_memory.ps1
```

### Hook 未生效

```powershell
# 检查 Hook 文件
Test-Path "C:\Users\34438\.openclaw\hooks\observational_memory.py"

# 重新复制
Copy-Item ".\hooks\observational_memory.py" "C:\Users\34438\.openclaw\hooks\observational_memory.py" -Force
```

### API 无法访问

```powershell
# 测试 API
Invoke-RestMethod -Uri "http://localhost:3000/api/sessions"
```

## 卸载

```powershell
# 停止服务
Stop-Process -Name "observational-memory" -Force

# 删除 Hook
Remove-Item "C:\Users\34438\.openclaw\hooks\observational_memory.py"

# 删除快捷方式
Remove-Item "$env:USERPROFILE\Desktop\Observational Memory.lnk"
```
