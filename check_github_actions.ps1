# check_github_actions.ps1 - 检查 GitHub Actions 状态

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Actions 构建状态" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "项目: kiss-kedaya/openclaw-observational-memory" -ForegroundColor Gray
Write-Host "Tag: v1.2.0" -ForegroundColor Gray
Write-Host ""

Write-Host "查看构建状态:" -ForegroundColor Yellow
Write-Host "  https://github.com/kiss-kedaya/openclaw-observational-memory/actions" -ForegroundColor Cyan
Write-Host ""

Write-Host "预编译版本下载:" -ForegroundColor Yellow
Write-Host "  Windows x64: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest/download/observational-memory-windows-x64.exe" -ForegroundColor Cyan
Write-Host "  macOS x64: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest/download/observational-memory-macos-x64" -ForegroundColor Cyan
Write-Host "  macOS ARM64: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest/download/observational-memory-macos-arm64" -ForegroundColor Cyan
Write-Host "  Linux x64: https://github.com/kiss-kedaya/openclaw-observational-memory/releases/latest/download/observational-memory-linux-x64" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  等待构建完成（约 10-15 分钟）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
