# Start Named Cloudflare Tunnel (Persistent URL)
# This tunnel survives restarts!

Write-Host "🚀 Starting Named Cloudflare Tunnel: lepetpal" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Connecting to Cloudflare..." -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ This tunnel has a PERMANENT URL!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Keep this window open while developing!" -ForegroundColor Yellow
Write-Host ""

# Run named tunnel
.\cloudflared.exe tunnel --config cloudflared-config.yml run lepetpal
