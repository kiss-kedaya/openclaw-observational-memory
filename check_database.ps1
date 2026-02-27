# check_database.ps1 - 检查数据库状态
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  检查 Observational Memory 数据库" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取会话列表
Write-Host "[1/2] 获取会话列表..." -ForegroundColor Yellow
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions" -Method Get
    Write-Host "  总会话数: $($sessions.Count)" -ForegroundColor Green
    
    if ($sessions.Count -gt 0) {
        Write-Host "  最新 5 个会话:" -ForegroundColor Gray
        $sessions | Select-Object -First 5 | ForEach-Object {
            Write-Host "    - $($_.id): messages=$($_.message_count), tokens=$($_.token_count)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# 检查观察数据
Write-Host "[2/2] 检查观察数据..." -ForegroundColor Yellow
if ($sessions.Count -gt 0) {
    $sessionId = $sessions[0].id
    Write-Host "  检查会话: $sessionId" -ForegroundColor Gray
    
    try {
        $observations = Invoke-RestMethod -Uri "http://localhost:3000/api/observations/$sessionId" -Method Get
        Write-Host "  观察数: $($observations.Count)" -ForegroundColor Green
        
        if ($observations.Count -gt 0) {
            Write-Host "  前 3 条观察:" -ForegroundColor Gray
            $observations | Select-Object -First 3 | ForEach-Object {
                Write-Host "    - $($_.priority): $($_.content.Substring(0, [Math]::Min(50, $_.content.Length)))..." -ForegroundColor Gray
            }
        } else {
            Write-Host "  ⚠️ 没有观察数据" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  检查完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
