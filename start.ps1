$ErrorActionPreference = "Stop"

Write-Host "🚀 启动 Observational Memory..." -ForegroundColor Green

# 检查是否已运行
$process = Get-Process -Name "observational-memory" -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "✅ Observational Memory 已在运行 (PID: $($process.Id))" -ForegroundColor Yellow
    Write-Host "🌐 访问: http://localhost:3000" -ForegroundColor Cyan
    exit 0
}

# 启动服务
Write-Host "🔧 启动服务..." -ForegroundColor Cyan
Start-Process -FilePath ".\target\release\observational-memory.exe" -WindowStyle Hidden

# 等待启动
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 验证启动
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Observational Memory 已启动" -ForegroundColor Green
    Write-Host "🌐 访问: http://localhost:3000" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ 服务可能仍在启动中，请稍候访问 http://localhost:3000" -ForegroundColor Yellow
}
