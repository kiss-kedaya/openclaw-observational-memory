# start_poller.ps1 - 启动 Session Poller
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Session Poller" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$env:PYTHONIOENCODING = "utf-8"

Write-Host "Polling OpenClaw sessions..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

uv run python session_poller.py
