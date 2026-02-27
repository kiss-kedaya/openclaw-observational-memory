# test_integration.ps1 - 测试 OpenClaw 集成
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🧪 测试 Observational Memory 集成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 测试服务启动
Write-Host "[1/4] 测试服务启动..." -ForegroundColor Yellow
.\start_observational_memory.ps1
Start-Sleep -Seconds 3

# 2. 测试 API
Write-Host "[2/4] 测试 API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get -TimeoutSec 5
    Write-Host "  ✅ API 测试通过: $($response.Count) 个会话" -ForegroundColor Green
} catch {
    Write-Host "  ❌ API 测试失败: $_" -ForegroundColor Red
    exit 1
}

# 3. 测试 Hook 文件
Write-Host "[3/4] 测试 Hook 文件..." -ForegroundColor Yellow
if (Test-Path "C:\Users\34438\.openclaw\hooks\observational_memory.py") {
    Write-Host "  ✅ Hook 文件存在" -ForegroundColor Green
} else {
    Write-Host "  ❌ Hook 文件不存在" -ForegroundColor Red
    exit 1
}

# 4. 测试桌面快捷方式
Write-Host "[4/4] 测试桌面快捷方式..." -ForegroundColor Yellow
if (Test-Path "$env:USERPROFILE\Desktop\Observational Memory.lnk") {
    Write-Host "  ✅ 桌面快捷方式存在" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ 桌面快捷方式不存在" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ 集成测试完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方法:" -ForegroundColor White
Write-Host "  1. OpenClaw Gateway 会自动启动 Observational Memory" -ForegroundColor Gray
Write-Host "  2. 所有对话会自动记录" -ForegroundColor Gray
Write-Host "  3. 访问 http://localhost:3000 查看记录" -ForegroundColor Gray
Write-Host "  4. 使用桌面快捷方式快速访问" -ForegroundColor Gray
Write-Host ""
