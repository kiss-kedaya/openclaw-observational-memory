# start_observational_memory.ps1
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🚀 Observational Memory 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已运行
$process = Get-Process -Name "observational-memory" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "[✅] Observational Memory 已在运行 (PID: $($process.Id))" -ForegroundColor Yellow
    Write-Host "[🌐] 访问: http://localhost:3000" -ForegroundColor Cyan
    exit 0
}

# 检查可执行文件
$exePath = ".\target\release\observational-memory.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "[❌] 未找到可执行文件: $exePath" -ForegroundColor Red
    Write-Host "[💡] 请先运行: cargo build --release" -ForegroundColor Yellow
    exit 1
}

# 启动服务
Write-Host "[→] 启动 Observational Memory..." -ForegroundColor Green
try {
    $proc = Start-Process -FilePath $exePath -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 2
    
    # 验证启动
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "[✅] Observational Memory 已启动 (PID: $($proc.Id))" -ForegroundColor Green
        Write-Host "[🌐] 访问: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "功能:" -ForegroundColor White
        Write-Host "  - 会话管理" -ForegroundColor Gray
        Write-Host "  - 观察记录" -ForegroundColor Gray
        Write-Host "  - 高级搜索" -ForegroundColor Gray
        Write-Host "  - 数据分析" -ForegroundColor Gray
        Write-Host "  - 工具建议" -ForegroundColor Gray
        Write-Host "  - 记忆管理" -ForegroundColor Gray
        Write-Host ""
    } catch {
        Write-Host "[⚠️] 服务启动中，请稍候..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[❌] 启动失败: $_" -ForegroundColor Red
    exit 1
}
