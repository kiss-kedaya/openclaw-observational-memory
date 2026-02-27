# test_save_messages.ps1 - 测试消息保存
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试消息保存功能" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$sessionId = "test-save-$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "[1/3] 创建测试会话..." -ForegroundColor Yellow
$body = @{
    session_id = $sessionId
    messages = @(
        @{
            role = "user"
            content = "This is a test message to verify message saving"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "Request body:" -ForegroundColor Gray
Write-Host $body -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK - Session created" -ForegroundColor Green
    Write-Host "  Response:" -ForegroundColor Gray
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Gray
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
    Write-Host "  Response: $($_.Exception.Response)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] 检查会话..." -ForegroundColor Yellow
try {
    $session = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get | Where-Object { $_.id -eq $sessionId }
    if ($session) {
        Write-Host "  OK - Session found" -ForegroundColor Green
        Write-Host "  message_count: $($session.message_count)" -ForegroundColor Gray
        Write-Host "  token_count: $($session.token_count)" -ForegroundColor Gray
    } else {
        Write-Host "  ERROR - Session not found" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/3] 检查数据库..." -ForegroundColor Yellow
Write-Host "  (需要手动检查 messages 表)" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
