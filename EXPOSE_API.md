# Exposing Flask Backend to Internet

Your friend's Next.js frontend needs to access your Flask backend over the internet.

## Quick Start (ngrok - Recommended)

### 1. Install ngrok
```bash
# Download from https://ngrok.com/download
# Or use winget:
winget install ngrok
```

### 2. Start Flask Backend
```bash
cd backend
python run_backend.py
```

Wait for:
```
* Running on http://127.0.0.1:5000
```

### 3. Expose with ngrok (New Terminal)
```bash
ngrok http 5000
```

You'll see:
```
Session Status                online
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

### 4. Share URL with Your Friend
```
https://abc123.ngrok.io
```

**That's it!** Your friend can now use this URL in their Next.js app.

---

## Alternative: Cloudflare Tunnel

### 1. Install cloudflared
```bash
winget install Cloudflare.cloudflared
```

### 2. Start Flask Backend
```bash
cd backend
python run_backend.py
```

### 3. Create Tunnel (New Terminal)
```bash
cloudflared tunnel --url http://localhost:5000
```

You'll get:
```
Your quick Tunnel has been created! Visit it at:
https://xyz-abc.trycloudflare.com
```

### 4. Share URL
```
https://xyz-abc.trycloudflare.com
```

---

## Next.js Integration

Your friend should update their Next.js app to use your public URL:

### Environment Variable (.env.local)
```bash
NEXT_PUBLIC_API_BASE=https://abc123.ngrok.io
```

### API Client
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:5000';

// Health check
const health = await fetch(`${API_BASE}/health`);

// Send command
const response = await fetch(`${API_BASE}/command`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'pick up the ball' })
});

// Video feed
<img src={`${API_BASE}/video_feed`} />
```

---

## Testing the Public API

### From Browser
```
https://abc123.ngrok.io/health
```

Should return:
```json
{"api": 1, "status": "ok", "version": "v0.1"}
```

### From cURL
```bash
curl https://abc123.ngrok.io/health

curl -X POST https://abc123.ngrok.io/command \
  -H "Content-Type: application/json" \
  -d '{"prompt": "pick up the ball"}'
```

---

## ngrok vs Cloudflare

| Feature | ngrok | Cloudflare |
|---------|-------|------------|
| **Setup** | Easier | Easy |
| **Stability** | Good | Better |
| **Speed** | Fast | Faster |
| **Free Tier** | 1 tunnel | Unlimited |
| **Custom Domain** | Paid | Free |
| **URL Changes** | Every restart | Every restart |
| **Best For** | Quick demos | Production-ish |

**Recommendation:** Use **ngrok** for hackathon - it's simpler and works great.

---

## Important Notes

### 1. Keep Backend Running
Your Flask backend must stay running while your friend develops:
```bash
# Keep this terminal open
python backend/run_backend.py
```

### 2. Keep Tunnel Running
Keep ngrok/cloudflared running in another terminal:
```bash
# Keep this terminal open too
ngrok http 5000
```

### 3. URL Changes on Restart
If you restart ngrok, the URL changes. Share the new URL with your friend.

### 4. Free Tier Limits
- **ngrok free:** 1 tunnel, 40 connections/min
- **Cloudflare free:** Unlimited tunnels

---

## Troubleshooting

### ngrok: "command not found"
```bash
# Restart terminal after installing
# Or add to PATH manually
```

### CORS Errors
Already fixed! Your Flask backend now has:
```python
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

### Video Feed Not Working
Video streaming works through ngrok/cloudflare! Just use:
```html
<img src="https://abc123.ngrok.io/video_feed" />
```

### Slow Performance
- ngrok free tier has some latency (~50-100ms)
- Cloudflare is usually faster
- For production, deploy to a cloud server

---

## Production Alternative (If Needed)

If you need a permanent URL, deploy to:

### Option 1: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Option 2: Render
1. Push to GitHub
2. Connect to Render
3. Deploy (free tier available)

### Option 3: Fly.io
```bash
# Install flyctl
winget install Fly.flyctl

# Deploy
fly launch
fly deploy
```

---

## Quick Reference

### Start Everything
```bash
# Terminal 1: Flask Backend
cd backend
python run_backend.py

# Terminal 2: ngrok
ngrok http 5000

# Share the ngrok URL with your friend
```

### API Endpoints (Public)
```
GET  https://abc123.ngrok.io/health
GET  https://abc123.ngrok.io/video_feed
POST https://abc123.ngrok.io/command
GET  https://abc123.ngrok.io/status/:id
POST https://abc123.ngrok.io/dispense_treat
POST https://abc123.ngrok.io/speak
```

---

## Security Notes (For Production)

⚠️ **Current setup is for hackathon/demo only!**

For production, add:
1. **API Key authentication**
2. **Rate limiting**
3. **HTTPS only**
4. **Specific CORS origins** (not `*`)
5. **Input validation**
6. **Logging/monitoring**

But for hackathon: **Current setup is fine!** 🚀
