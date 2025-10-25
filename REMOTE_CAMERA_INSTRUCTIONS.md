# Remote Camera Setup - For Your Friend 📹

## What This Does

Your friend runs a simple Python script on their computer with a webcam. It streams the video over your local network to your pet training app.

## Setup Instructions (Send to Your Friend)

### Step 1: Install Requirements

```bash
pip install flask opencv-python
```

### Step 2: Download and Run the Script

1. Get the `remote_camera_server.py` file
2. Open terminal/command prompt in that folder
3. Run:
   ```bash
   python remote_camera_server.py
   ```

### Step 3: Note the URL

The script will show something like:
```
🎥 Remote Camera Server Starting...
✅ Camera ready!

📺 View stream in browser:
   http://192.168.1.150:5000

🔗 Use this URL in your pet training app:
   http://192.168.1.150:5000/video
```

**Send you that URL!** (the one ending in `/video`)

### Step 4: Test It Works

Open a browser and go to `http://192.168.1.150:5000` (use their actual IP)

You should see the webcam feed!

## On Your Side (Your Computer)

### Option 1: Quick Test (No Code Changes)

1. Open your app in browser
2. Open browser console (F12)
3. Run:
   ```javascript
   localStorage.setItem('videoStreamURL', 'http://192.168.1.150:5000/video');
   ```
   (Use the URL your friend gave you)
4. Refresh the page
5. Go to Live page - should see their camera!

### Option 2: Update Config File

Edit `Pet Training Web App/src/config/env.ts`:

```typescript
export const config = {
  apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  videoStreamURL: 'http://192.168.1.150:5000/video', // Your friend's camera
  wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
}
```

Then restart your frontend:
```bash
cd "Pet Training Web App"
npm run dev
```

## Troubleshooting

### "Can't connect to camera"

**Check:**
- Both computers on same WiFi network
- Firewall not blocking port 5000
- Try the IP address in a browser first

**Fix:**
Your friend can try:
```bash
# Windows - allow through firewall
netsh advfirewall firewall add rule name="Camera Server" dir=in action=allow protocol=TCP localport=5000

# Or just disable firewall temporarily for testing
```

### "Camera not found"

The script tries camera indices 0, 1, 2. If still not working:

Edit `remote_camera_server.py` line 17:
```python
for index in [0, 1, 2, 3, 4]:  # Try more indices
```

### "Stream is laggy"

Reduce quality in `remote_camera_server.py` line 35:
```python
ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])  # Lower quality
```

Or reduce resolution line 25:
```python
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Smaller
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Smaller
```

## Network Setup

### Same WiFi Network (Easiest)
- Both computers connected to same WiFi
- Use local IP (192.168.x.x)
- Works immediately

### Different Networks (Advanced)
Need to set up port forwarding or use ngrok:

```bash
# Your friend installs ngrok
ngrok http 5000

# Gives you a public URL like:
# https://abc123.ngrok.io

# Use: https://abc123.ngrok.io/video
```

## For Demo/Hackathon

This setup is perfect because:
- ✅ Takes 5 minutes to set up
- ✅ Works reliably (no buffer issues)
- ✅ Can position camera anywhere
- ✅ Better quality than most built-in webcams
- ✅ Looks professional

## Alternative: Use Phone Instead

If your friend doesn't have a webcam, they can use their phone:
1. Install "IP Webcam" app (Android) or "EpocCam" (iOS)
2. Start server in app
3. Use the URL shown in the app

Same process, even easier!
