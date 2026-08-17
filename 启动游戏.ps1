# 星尘回响 启动脚本
Write-Host "========================================"
Write-Host "    星尘回响  Echoes of Stardust"
Write-Host "========================================"
Write-Host ""

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python not found. Please install Python and add to PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Python ready" -ForegroundColor Green

# 检查 pygame
try {
    python -c "import pygame; print('[OK] pygame installed')" 2>$null | Out-Null
    Write-Host "[OK] pygame installed" -ForegroundColor Green
}
catch {
    Write-Host "[WARN] pygame not found, installing..." -ForegroundColor Yellow
    pip install pygame
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] pygame install failed. Run manually: pip install pygame" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] pygame installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting game..."
Write-Host ""

# 启动游戏
python run.py
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================"
if ($exitCode -eq 0) {
    Write-Host "Game exited normally" -ForegroundColor Green
} else {
    Write-Host "Game crashed with code: $exitCode" -ForegroundColor Red
    Write-Host "Check error output above" -ForegroundColor Yellow
}
Write-Host "========================================"
Write-Host ""
Read-Host "Press Enter to exit"