# Start Cloudflare Tunnel for LePetPal Backend
# Unlimited bandwidth on free tier!

Write-Host "🚀 Starting Cloudflare Tunnel for LePetPal Backend" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Creating tunnel to http://localhost:5000..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Keep this window open while your friend is developing!" -ForegroundColor Yellow
Write-Host ""

# Start quick tunnel
.\cloudflared.exe tunnel --url http://localhost:5000
