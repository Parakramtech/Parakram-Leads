param(
  [string]$OutputDir = (Join-Path $PSScriptRoot "dist")
)

$ErrorActionPreference = "Stop"
$start = Get-Date

Write-Host "=== Parakram VPS Build v3.0.0 ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install npm deps (if needed)
$dashDir = Join-Path $PSScriptRoot "dashboard"
$wixDir = Join-Path $PSScriptRoot "wix"
$distDir = $OutputDir

Push-Location $dashDir
try {
  if (-not (Test-Path "node_modules/.package-lock.json")) {
    Write-Host "[1/6] Installing npm dependencies..." -ForegroundColor Yellow
    npm install --ignore-scripts 2>&1 | Out-Null
    Write-Host "  ✓ npm install" -ForegroundColor Green
  }

  # Step 2: Build frontend
    Write-Host "[2/6] Building React frontend..." -ForegroundColor Yellow
  npm run build 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
  Write-Host "  ✓ Frontend built (dist/frontend/)" -ForegroundColor Green

  # Step 3: Bundle backend
    Write-Host "[3/6] Bundling Node.js backend..." -ForegroundColor Yellow
  node scripts/bundle-backend.mjs 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Backend bundle failed" }
  Write-Host "  ✓ Backend bundled (dist/bundle/backend.cjs)" -ForegroundColor Green

  # Step 4: Download Node.js runtime
  if (-not (Test-Path "dist/runtime/node.exe")) {
    Write-Host "[4/6] Downloading Node.js runtime..." -ForegroundColor Yellow
    node scripts/download-node.mjs 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Node.js download failed" }
  }
  Write-Host "  ✓ Node.js runtime ready ($((Get-Item 'dist/runtime/node.exe').Length / 1MB) MB)" -ForegroundColor Green

  # Step 4b: Download cloudflared (bundled so no install-time download needed)
  if (-not (Test-Path "dist/runtime/cloudflared.exe")) {
    Write-Host "[4b/6] Downloading cloudflared..." -ForegroundColor Yellow
    node scripts/download-cloudflared.mjs 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "cloudflared download failed" }
  }
  Write-Host "  ✓ cloudflared ready ($((Get-Item 'dist/runtime/cloudflared.exe').Length / 1MB) MB)" -ForegroundColor Green

  # Step 4c: Download WinSW (wraps the Node backend as a real Windows service)
  if (-not (Test-Path "dist/runtime/ParakramVPS-svc.exe")) {
    Write-Host "[4c/6] Downloading WinSW..." -ForegroundColor Yellow
    node scripts/download-winsw.mjs 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "WinSW download failed" }
  }
  Write-Host "  ✓ WinSW ready ($((Get-Item 'dist/runtime/ParakramVPS-svc.exe').Length / 1MB) MB)" -ForegroundColor Green
}
finally { Pop-Location }

# Step 5: Generate WiX fragment for auto-discovered frontend assets
Write-Host "[5/6] Generating WiX file list..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "scripts\generate-wxs.ps1") 2>&1 | Out-Null
Write-Host "  ✓ File list generated" -ForegroundColor Green

# Step 6: Build MSI
Write-Host "[6/6] Building WiX MSI installer..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $distDir -Force | Out-Null
$msiPath = Join-Path $distDir "ParakramVPS.msi"

wix build (Join-Path $wixDir "ParakramVPS.wxs") `
  (Join-Path $wixDir "GeneratedFiles.wxs") `
  -out $msiPath `
  -bindpath (Join-Path $dashDir "dist") `
  -arch x64 2>&1

if ($LASTEXITCODE -ne 0) { throw "MSI build failed (see errors above)" }

$msiSize = (Get-Item $msiPath).Length / 1MB
$elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
Write-Host "  ✓ MSI built (${msiSize:F1} MB)" -ForegroundColor Green
Write-Host ""
Write-Host "=== Build complete in ${elapsed}s ===" -ForegroundColor Cyan
Write-Host "Output: $msiPath" -ForegroundColor White
