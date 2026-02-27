# sync_memory.ps1 - 增量同步 Memory 文件
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  同步 Memory 文件到 Observational Memory" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$memoryPath = "C:\Users\34438\.openclaw\workspace\memory"
$apiUrl = "http://localhost:3000/api/sessions"

# 检查服务是否运行
try {
    $null = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
} catch {
    Write-Host "[ERROR] Observational Memory 服务未运行" -ForegroundColor Red
    Write-Host "[INFO] 请先运行: .\start.ps1" -ForegroundColor Yellow
    exit 1
}

# 同步今日日志
$today = Get-Date -Format "yyyy-MM-dd"
$todayFile = Join-Path $memoryPath "$today.md"

if (Test-Path $todayFile) {
    Write-Host "[→] 同步今日日志: $today.md..." -ForegroundColor Cyan
    
    try {
        $content = Get-Content $todayFile -Raw -Encoding UTF8
        
        $body = @{
            session_id = "daily-log-$today"
            messages = @(
                @{
                    role = "system"
                    content = $content
                    timestamp = (Get-Date).ToUniversalTime().ToString("o")
                }
            )
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        Write-Host "  [✓] 今日日志已同步" -ForegroundColor Green
    } catch {
        Write-Host "  [✗] 同步失败: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] 今日日志文件不存在: $todayFile" -ForegroundColor Yellow
}

# 同步 MEMORY.md
$memoryFile = Join-Path $memoryPath "..\MEMORY.md"
if (Test-Path $memoryFile) {
    Write-Host "[→] 同步 MEMORY.md..." -ForegroundColor Cyan
    
    try {
        $content = Get-Content $memoryFile -Raw -Encoding UTF8
        
        $body = @{
            session_id = "global-memory"
            messages = @(
                @{
                    role = "system"
                    content = $content
                    timestamp = (Get-Date).ToUniversalTime().ToString("o")
                }
            )
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        Write-Host "  [✓] MEMORY.md 已同步" -ForegroundColor Green
    } catch {
        Write-Host "  [✗] 同步失败: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] MEMORY.md 文件不存在: $memoryFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  同步完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
