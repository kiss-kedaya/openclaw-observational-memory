# check_database_detailed.ps1 - 详细检查数据库
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  数据库详细检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查会话
Write-Host "[1/4] 检查会话..." -ForegroundColor Yellow
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get
    Write-Host "  总会话数: $($sessions.Count)" -ForegroundColor Gray
    
    $withMessages = $sessions | Where-Object { $_.message_count -gt 0 }
    $withoutMessages = $sessions | Where-Object { $_.message_count -eq 0 }
    
    Write-Host "  有消息: $($withMessages.Count)" -ForegroundColor Green
    Write-Host "  无消息: $($withoutMessages.Count)" -ForegroundColor Red
    
    Write-Host ""
    Write-Host "  有消息的会话:" -ForegroundColor Green
    $withMessages | ForEach-Object {
        Write-Host "    - $($_.id): $($_.message_count) messages, $($_.token_count) tokens" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "  最近创建的无消息会话 (前 5 个):" -ForegroundColor Yellow
    $withoutMessages | Select-Object -First 5 | ForEach-Object {
        Write-Host "    - $($_.id): created $($_.created_at)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[2/4] 检查 messages 表..." -ForegroundColor Yellow
Write-Host "  (需要直接查询数据库)" -ForegroundColor Gray

Write-Host ""
Write-Host "[3/4] 检查 Hook 状态..." -ForegroundColor Yellow
try {
    $hookStatus = openclaw hooks list 2>&1 | Select-String "observational-memory"
    Write-Host "  $hookStatus" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4/4] 检查服务状态..." -ForegroundColor Yellow
try {
    $process = Get-Process -Name "observational-memory" -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  PID: $($process.Id)" -ForegroundColor Green
        Write-Host "  运行时间: $([math]::Round((New-TimeSpan -Start $process.StartTime).TotalMinutes, 1)) 分钟" -ForegroundColor Gray
    } else {
        Write-Host "  服务未运行" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR - $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  检查完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
