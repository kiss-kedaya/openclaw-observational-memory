# diagnose.ps1 - 完整诊断脚本
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Observational Memory 诊断" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查服务状态
Write-Host "[1/6] 检查服务状态..." -ForegroundColor Yellow
$process = Get-Process -Name "observational-memory" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "  OK - 服务运行中 (PID: $($process.Id))" -ForegroundColor Green
} else {
    Write-Host "  ERROR - 服务未运行" -ForegroundColor Red
    Write-Host "  请运行: .\start_observational_memory.ps1" -ForegroundColor Yellow
    exit 1
}

# 2. 测试 API 连接
Write-Host "[2/6] 测试 API 连接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/sessions" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  OK - API 可访问" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - API 无法访问: $_" -ForegroundColor Red
    exit 1
}

# 3. 获取会话列表
Write-Host "[3/6] 获取会话列表..." -ForegroundColor Yellow
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get
    Write-Host "  OK - 共 $($sessions.Count) 个会话" -ForegroundColor Green
    if ($sessions.Count -gt 0) {
        Write-Host "  最新会话:" -ForegroundColor Gray
        $sessions | Select-Object -First 3 | ForEach-Object {
            Write-Host "    - $($_.id) (创建于: $($_.created_at))" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  ERROR - 获取会话失败: $_" -ForegroundColor Red
}

# 4. 检查 Hook 文件
Write-Host "[4/6] 检查 Hook 文件..." -ForegroundColor Yellow
$hookPath = "C:\Users\34438\.openclaw\hooks\observational_memory.py"
if (Test-Path $hookPath) {
    Write-Host "  OK - Hook 文件存在" -ForegroundColor Green
} else {
    Write-Host "  ERROR - Hook 文件不存在" -ForegroundColor Red
    Write-Host "  请运行: Copy-Item .\hooks\observational_memory.py $hookPath -Force" -ForegroundColor Yellow
}

# 5. 测试 Hook 功能
Write-Host "[5/6] 测试 Hook 功能..." -ForegroundColor Yellow
try {
    python test_hook.py 2>&1 | Out-Null
    Write-Host "  OK - Hook 测试通过" -ForegroundColor Green
} catch {
    Write-Host "  WARN - Hook 测试失败: $_" -ForegroundColor Yellow
}

# 6. 测试前端
Write-Host "[6/6] 测试前端..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  OK - 前端可访问" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - 前端无法访问: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  诊断完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "建议:" -ForegroundColor White
Write-Host "  1. 打开 http://localhost:3000" -ForegroundColor Gray
Write-Host "  2. 点击左侧 '会话管理' 菜单" -ForegroundColor Gray
Write-Host "  3. 应该能看到 $($sessions.Count) 个会话" -ForegroundColor Gray
Write-Host "  4. 如果没有，请刷新页面 (Ctrl+F5)" -ForegroundColor Gray
Write-Host ""
