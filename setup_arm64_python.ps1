# Setup ARM64 Python for LePetPal
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARM64 Python Setup for LePetPal" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running on ARM64
$arch = (Get-WmiObject Win32_Processor).Architecture
if ($arch -ne 12) {  # 12 = ARM64
    Write-Host "ERROR: Not running on ARM64 architecture!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/5] Checking for ARM64 Python installation..." -ForegroundColor Yellow

# Common ARM64 Python installation paths
$arm64PythonPaths = @(
    "C:\Users\henri\AppData\Local\Programs\Python\Python313-arm64\python.exe",
    "C:\Program Files\Python313-arm64\python.exe",
    "C:\Program Files\Python312-arm64\python.exe",
    "C:\Program Files\Python311-arm64\python.exe",
    "C:\Program Files\Python310-arm64\python.exe",
    "C:\Python312-arm64\python.exe",
    "C:\Python311-arm64\python.exe"
)

$arm64Python = $null
foreach ($path in $arm64PythonPaths) {
    if (Test-Path $path) {
        $arm64Python = $path
        Write-Host "  Found ARM64 Python: $path" -ForegroundColor Green
        break
    }
}

if (-not $arm64Python) {
    Write-Host "  ARM64 Python not found!" -ForegroundColor Red
    Write-Host "`n  Please install ARM64 Python manually:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://www.python.org/downloads/windows/" -ForegroundColor White
    Write-Host "  2. Download 'Windows installer (ARM64)' for Python 3.12" -ForegroundColor White
    Write-Host "  3. Install it (check 'Add to PATH')" -ForegroundColor White
    Write-Host "  4. Run this script again" -ForegroundColor White
    Write-Host "`n  Or download directly:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/ftp/python/3.12.4/python-3.12.4-arm64.exe" -ForegroundColor White
    
    # Offer to open download page
    $open = Read-Host "`n  Open download page in browser? (y/n)"
    if ($open -eq 'y') {
        Start-Process "https://www.python.org/downloads/windows/"
    }
    exit 1
}

# Verify it's actually ARM64
Write-Host "`n[2/5] Verifying Python architecture..." -ForegroundColor Yellow
$pythonArch = & $arm64Python -c "import platform; print(platform.machine())"
if ($pythonArch -ne "ARM64") {
    Write-Host "  ERROR: Python reports architecture as '$pythonArch', not ARM64!" -ForegroundColor Red
    exit 1
}
Write-Host "  Verified: Python is native ARM64" -ForegroundColor Green

# Create new ARM64 virtual environment
Write-Host "`n[3/5] Creating ARM64 virtual environment..." -ForegroundColor Yellow
$venvPath = ".venv_arm64"
if (Test-Path $venvPath) {
    Write-Host "  Removing existing $venvPath..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $venvPath
}

& $arm64Python -m venv $venvPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}
Write-Host "  Created: $venvPath" -ForegroundColor Green

# Activate and install dependencies
Write-Host "`n[4/5] Installing dependencies..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

Write-Host "  Upgrading pip..." -ForegroundColor Cyan
& python -m pip install --upgrade pip

Write-Host "  Installing requirements..." -ForegroundColor Cyan
& pip install -r backend\requirements.txt

Write-Host "  Installing torch-directml for GPU acceleration..." -ForegroundColor Cyan
& pip install torch-directml

Write-Host "  Installing transformers and dependencies..." -ForegroundColor Cyan
& pip install transformers num2words

# Verify installation
Write-Host "`n[5/5] Verifying installation..." -ForegroundColor Yellow
& python backend\tools\verify_arm64_gpu.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTo use ARM64 Python:" -ForegroundColor Yellow
Write-Host "  1. Activate: .\.venv_arm64\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run backend: python backend\run_backend.py" -ForegroundColor White
Write-Host "`nExpected performance improvement: 2-5x faster!" -ForegroundColor Green
