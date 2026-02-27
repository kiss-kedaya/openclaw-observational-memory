# test_message_sent.ps1 - 测试 message:sent 事件
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试 message:sent 事件" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$sessionId = "test-sent-$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "[1/2] 发送用户消息..." -ForegroundColor Yellow
$body = @{
    session_id = $sessionId
    messages = @(
        @{
            role = "user"
            content = "Test user message"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK - User message saved" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/2] 发送 AI 回复..." -ForegroundColor Yellow
$body = @{
    session_id = $sessionId
    messages = @(
        @{
            role = "assistant"
            content = "Test AI response"
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK - AI response saved" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "检查会话..." -ForegroundColor Yellow
try {
    $session = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get | Where-Object { $_.id -eq $sessionId }
    if ($session) {
        Write-Host "  message_count: $($session.message_count)" -ForegroundColor Gray
        Write-Host "  token_count: $($session.token_count)" -ForegroundColor Gray
        
        if ($session.message_count -eq 2) {
            Write-Host "  OK - Both messages saved" -ForegroundColor Green
        } else {
            Write-Host "  ERROR - Expected 2 messages, got $($session.message_count)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
