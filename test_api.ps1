# test_api.ps1 - 测试 API 创建会话
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Observational Memory API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 测试服务是否运行
Write-Host "[1/3] Testing service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  OK - Service is running" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - Service not running" -ForegroundColor Red
    Write-Host "  Please run: .\start_observational_memory.ps1" -ForegroundColor Yellow
    exit 1
}

# 2. 创建测试会话
Write-Host "[2/3] Creating test session..." -ForegroundColor Yellow
$sessionId = "manual-test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$body = @{
    session_id = $sessionId
    messages = @(
        @{
            role = "user"
            content = "Test message - Manual creation at $(Get-Date)"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK - Session created: $sessionId" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - Failed to create session: $_" -ForegroundColor Red
    exit 1
}

# 3. 验证会话
Write-Host "[3/3] Verifying session..." -ForegroundColor Yellow
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get
    $found = $sessions | Where-Object { $_.id -eq $sessionId }
    if ($found) {
        Write-Host "  OK - Session verified: $sessionId" -ForegroundColor Green
    } else {
        Write-Host "  WARN - Session not found in list" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ERROR - Failed to verify: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test completed" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Open http://localhost:3000" -ForegroundColor Gray
Write-Host "  2. Check if session $sessionId appears" -ForegroundColor Gray
Write-Host ""
