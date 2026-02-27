# test_chinese_encoding.ps1 - 测试中文编码
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试中文编码" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$sessionId = "test-chinese-$(Get-Date -Format 'yyyyMMddHHmmss')"
$chineseText = "这是一个中文测试消息，用于验证UTF-8编码是否正常工作。"

Write-Host "[1/3] 发送中文消息..." -ForegroundColor Yellow
$body = @{
    session_id = $sessionId
    messages = @(
        @{
            role = "user"
            content = $chineseText
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Post -Body $body -ContentType "application/json; charset=utf-8"
    Write-Host "  OK - Session created" -ForegroundColor Green
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] 读取观察记录..." -ForegroundColor Yellow
try {
    $observations = Invoke-RestMethod -Uri "http://localhost:3000/api/observations/$sessionId" -Method Get
    if ($observations.Count -gt 0) {
        Write-Host "  观察记录内容:" -ForegroundColor Gray
        $observations | ForEach-Object {
            Write-Host "    $($_.content)" -ForegroundColor Gray
        }
        
        # 检查是否有乱码
        $hasGarbled = $observations | Where-Object { $_.content -match '�' }
        if ($hasGarbled) {
            Write-Host "  ERROR - 检测到乱码" -ForegroundColor Red
        } else {
            Write-Host "  OK - 中文显示正常" -ForegroundColor Green
        }
    } else {
        Write-Host "  WARN - 没有观察记录" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/3] 对比原始文本..." -ForegroundColor Yellow
Write-Host "  原始: $chineseText" -ForegroundColor Gray
if ($observations.Count -gt 0) {
    Write-Host "  读取: $($observations[0].content)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
