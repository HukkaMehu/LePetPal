# Start Cloudflare Tunnel and save URL to file
# This makes it easy to share the URL with your friend

Write-Host "🚀 Starting Cloudflare Tunnel for LePetPal Backend" -ForegroundColor Cyan
Write-Host ""

# Start cloudflared and capture output
$process = Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel", "--url", "http://localhost:5000" -PassThru -NoNewWindow -RedirectStandardOutput "cloudflare_output.txt" -RedirectStandardError "cloudflare_error.txt"

Write-Host "⏳ Waiting for tunnel to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Read the output and extract URL
$output = Get-Content "cloudflare_output.txt" -Raw
if ($output -match "https://[a-z0-9\-]+\.trycloudflare\.com") {
    $url = $matches[0]
    
    # Save URL to file
    $url | Out-File -FilePath "CLOUDFLARE_URL.txt" -Encoding UTF8
    
    Write-Host ""
    Write-Host "✅ Tunnel is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Your public URL:" -ForegroundColor Cyan
    Write-Host "   $url" -ForegroundColor White
    Write-Host ""
    Write-Host "💾 URL saved to: CLOUDFLARE_URL.txt" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔗 Share this URL with your friend!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Keep this window open while developing!" -ForegroundColor Yellow
    Write-Host ""
    
    # Keep script running
    Write-Host "Press Ctrl+C to stop the tunnel..." -ForegroundColor Gray
    Wait-Process -Id $process.Id
} else {
    Write-Host "❌ Failed to get tunnel URL. Check cloudflare_output.txt for details." -ForegroundColor Red
}
