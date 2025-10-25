# External Camera Setup - Easy Solution! 📱

Instead of fighting with the in-memory buffer, use an external camera (phone/tablet/another computer) to stream video.

## Why This Works Better

- ✅ No memory buffer issues
- ✅ Better camera quality (phones have great cameras)
- ✅ More flexible positioning
- ✅ Works immediately
- ✅ Can still record clips (just won't have the last 5 minutes buffered)

## Option 1: Use Your Phone (Recommended)

### Android - IP Webcam App

1. **Install IP Webcam** (free on Play Store)
2. Open app, scroll down, click "Start server"
3. App shows URL like: `http://192.168.1.100:8080`
4. Your video stream is at: `http://192.168.1.100:8080/video`

### iOS - EpocCam or DroidCam

1. **Install EpocCam** or **DroidCam** from App Store
2. Follow app instructions to start streaming
3. Note the IP address and port shown

### Configure Your App

**Option A: Direct URL (Quick Test)**

Just open your browser and go to:
```
http://localhost:3000
```

Then in browser console, temporarily override:
```javascript
localStorage.setItem('videoStreamURL', 'http://192.168.1.100:8080/video');
```

Refresh page - you should see your phone's camera!

**Option B: Update Config File**

Edit `Pet Training Web App/src/config/env.ts`:

```typescript
export const config = {
  // ... other config ...
  videoStreamURL: 'http://192.168.1.100:8080/video', // Your phone's IP
}
```

## Option 2: Use OBS Studio (Advanced)

If you want more control:

1. **Install OBS Studio** on computer with webcam
2. **Install OBS WebSocket plugin**
3. Set up scene with webcam
4. Use OBS's built-in streaming or RTMP output
5. Point your app to the OBS stream URL

## Option 3: Use Another Computer's Webcam

On the computer with webcam, run a simple Python server:

```python
# simple_camera_server.py
import cv2
from flask import Flask, Response

app = Flask(__name__)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

Run it:
```bash
pip install flask opencv-python
python simple_camera_server.py
```

Then use `http://[computer-ip]:8080/video` in your app.

## Testing Your Stream

1. **Check stream works** - Open in browser:
   ```
   http://192.168.1.100:8080/video
   ```
   You should see the video feed.

2. **Update your app** - Use one of the config methods above

3. **Open Live page** - Should show your external camera!

## For Demo/Hackathon

The **phone camera** option is perfect because:
- Takes 2 minutes to set up
- Better quality than most webcams
- Easy to position anywhere
- Looks professional
- No code changes needed (just config)

## Troubleshooting

**Can't connect to phone stream?**
- Make sure phone and computer on same WiFi
- Check firewall isn't blocking the port
- Try the IP address shown in the phone app

**Stream is laggy?**
- Reduce resolution in phone app settings
- Make sure WiFi signal is strong
- Close other apps on phone

**CORS errors?**
- Phone camera apps usually don't have CORS issues
- If you do, add CORS headers in your backend proxy

## Next Steps

Once you have external camera working:
1. Clips will still work (just won't have buffer)
2. Live view works perfectly
3. AI detection can still process frames
4. Much more reliable than in-memory buffer

Want me to help you set up the phone camera stream?
