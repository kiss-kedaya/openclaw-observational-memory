# import_memory.ps1 - 批量导入 Memory 文件
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  导入 Memory 文件到 Observational Memory" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$memoryPath = "C:\Users\34438\.openclaw\workspace\memory"
$apiUrl = "http://localhost:3000/api/sessions"

# 检查目录是否存在
if (-not (Test-Path $memoryPath)) {
    Write-Host "[ERROR] Memory 目录不存在: $memoryPath" -ForegroundColor Red
    exit 1
}

# 获取所有 .md 文件
$files = Get-ChildItem $memoryPath -Filter "*.md" -ErrorAction SilentlyContinue

if ($files.Count -eq 0) {
    Write-Host "[WARN] 未找到任何 .md 文件" -ForegroundColor Yellow
    exit 0
}

Write-Host "[INFO] 找到 $($files.Count) 个文件" -ForegroundColor White
Write-Host ""

$imported = 0
$failed = 0

foreach ($file in $files) {
    try {
        Write-Host "[→] 导入: $($file.Name)..." -ForegroundColor Cyan
        
        # 读取文件内容
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        # 创建会话
        $body = @{
            session_id = "memory-$($file.BaseName)"
            messages = @(
                @{
                    role = "system"
                    content = $content
                    timestamp = $file.LastWriteTime.ToUniversalTime().ToString("o")
                }
            )
        } | ConvertTo-Json -Depth 10
        
        # 发送到 API
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        
        Write-Host "  [✓] 成功: $($file.Name)" -ForegroundColor Green
        $imported++
        
        # 避免请求过快
        Start-Sleep -Milliseconds 100
        
    } catch {
        Write-Host "  [✗] 失败: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  导入完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "成功: $imported 个文件" -ForegroundColor Green
Write-Host "失败: $failed 个文件" -ForegroundColor Red
Write-Host ""
