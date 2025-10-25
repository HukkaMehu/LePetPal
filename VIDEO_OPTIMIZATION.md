# Video Stream Optimization Guide

## Problem: MJPEG Stream Too Slow Over Internet

MJPEG over ngrok causes delays because:
- Large file sizes (uncompressed JPEGs)
- High bandwidth usage (~5-10 Mbps)
- ngrok adds 50-100ms latency per frame

## Solution: Optimized MJPEG Stream

We've added optimization parameters to reduce bandwidth and improve performance.

---

## Usage

### Default (Optimized for Internet)
```
https://your-ngrok-url.ngrok-free.app/video_feed
```

**Defaults:**
- Quality: 50% (good balance)
- Scale: 0.5x (640x360 from 1280x720)
- FPS: 10 (smooth enough for demo)
- **Bandwidth: ~500 KB/s** (10x reduction!)

---

## Custom Parameters

### Ultra-Low Bandwidth (for slow connections)
```
/video_feed?quality=30&scale=0.3&fps=5
```
- Quality: 30% (lower quality)
- Scale: 0.3x (384x216)
- FPS: 5 (choppy but works)
- **Bandwidth: ~100 KB/s**

### Balanced (recommended)
```
/video_feed?quality=50&scale=0.5&fps=10
```
- Quality: 50%
- Scale: 0.5x (640x360)
- FPS: 10
- **Bandwidth: ~500 KB/s**

### Higher Quality (if connection is good)
```
/video_feed?quality=70&scale=0.7&fps=15
```
- Quality: 70%
- Scale: 0.7x (896x504)
- FPS: 15
- **Bandwidth: ~1.5 MB/s**

### Full Quality (local network only)
```
/video_feed?quality=90&scale=1.0&fps=30
```
- Quality: 90%
- Scale: 1.0x (full resolution)
- FPS: 30
- **Bandwidth: ~5 MB/s**

---

## Next.js Integration

### Option 1: Use Query Parameters
```tsx
const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

// Optimized for internet
<img src={`${API_BASE}/video_feed?quality=50&scale=0.5&fps=10`} />

// Ultra-low bandwidth
<img src={`${API_BASE}/video_feed?quality=30&scale=0.3&fps=5`} />
```

### Option 2: User-Controlled Quality
```tsx
const [quality, setQuality] = useState(50);
const [scale, setScale] = useState(0.5);
const [fps, setFps] = useState(10);

const videoUrl = `${API_BASE}/video_feed?quality=${quality}&scale=${scale}&fps=${fps}`;

return (
  <div>
    <img src={videoUrl} />
    
    <div>
      <label>Quality: {quality}%</label>
      <input 
        type="range" 
        min="10" 
        max="90" 
        value={quality} 
        onChange={(e) => setQuality(e.target.value)} 
      />
    </div>
    
    <div>
      <label>Size: {scale}x</label>
      <input 
        type="range" 
        min="0.3" 
        max="1.0" 
        step="0.1"
        value={scale} 
        onChange={(e) => setScale(e.target.value)} 
      />
    </div>
    
    <div>
      <label>FPS: {fps}</label>
      <input 
        type="range" 
        min="5" 
        max="30" 
        value={fps} 
        onChange={(e) => setFps(e.target.value)} 
      />
    </div>
  </div>
);
```

---

## Performance Comparison

| Settings | Resolution | Bandwidth | Latency | Use Case |
|----------|-----------|-----------|---------|----------|
| **Ultra-Low** | 384x216 | ~100 KB/s | ~200ms | Slow 3G |
| **Low** | 480x270 | ~300 KB/s | ~150ms | 4G |
| **Balanced** ✅ | 640x360 | ~500 KB/s | ~100ms | Good WiFi/4G |
| **High** | 896x504 | ~1.5 MB/s | ~80ms | Fast WiFi |
| **Full** | 1280x720 | ~5 MB/s | ~50ms | Local only |

---

## Alternative: Snapshot Mode

If video is still too slow, use snapshot mode instead:

### Backend: Add Snapshot Endpoint
```python
@app.get("/snapshot")
def snapshot():
    ok, frame = camera.read()
    if not ok:
        return jsonify({"error": "Camera not available"}), 500
    
    # Resize and compress
    scale = float(request.args.get("scale", "0.5"))
    quality = int(request.args.get("quality", "70"))
    
    if scale != 1.0:
        new_width = int(frame.shape[1] * scale)
        new_height = int(frame.shape[0] * scale)
        frame = cv2.resize(frame, (new_width, new_height))
    
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    ret, jpeg = cv2.imencode('.jpg', frame, encode_params)
    
    return Response(jpeg.tobytes(), mimetype='image/jpeg')
```

### Frontend: Poll for Snapshots
```tsx
const [snapshot, setSnapshot] = useState('');

useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch(`${API_BASE}/snapshot?quality=60&scale=0.5`);
    const blob = await response.blob();
    setSnapshot(URL.createObjectURL(blob));
  }, 500); // Update every 500ms (2 FPS)
  
  return () => clearInterval(interval);
}, []);

return <img src={snapshot} />;
```

**Pros:**
- ✅ Much lower bandwidth
- ✅ Better control over update rate
- ✅ No streaming overhead

**Cons:**
- ❌ Not real-time video
- ❌ Choppy (but acceptable for demo)

---

## Recommended Settings for ngrok

```
/video_feed?quality=40&scale=0.5&fps=8
```

This gives:
- **Bandwidth: ~400 KB/s**
- **Latency: ~150ms**
- **Quality: Acceptable for demo**

---

## Testing

Test different settings:
```bash
# In browser
https://your-ngrok-url.ngrok-free.app/video_feed?quality=50&scale=0.5&fps=10

# Check bandwidth in browser DevTools:
# Network tab → Click on video_feed → See transfer size
```

---

## Summary

**For hackathon over ngrok, use:**
```
/video_feed?quality=40&scale=0.5&fps=8
```

This reduces bandwidth by **90%** while maintaining acceptable quality for demo! 🚀
