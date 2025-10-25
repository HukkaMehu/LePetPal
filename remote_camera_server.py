"""
Remote Camera Server
Run this on a computer with a webcam to stream video to the pet training app.

Usage:
    pip install flask opencv-python
    python remote_camera_server.py

Then use the URL shown in your pet training app config.
"""
import cv2
from flask import Flask, Response
import socket

app = Flask(__name__)

# Try to open webcam
camera = None
for index in [0, 1, 2]:  # Try multiple camera indices
    test_camera = cv2.VideoCapture(index)
    if test_camera.isOpened():
        camera = test_camera
        print(f"✅ Found webcam at index {index}")
        break
    test_camera.release()

if camera is None:
    print("❌ No webcam found!")
    exit(1)

# Set camera properties for better performance
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)

def generate_frames():
    """Generate video frames from webcam."""
    while True:
        success, frame = camera.read()
        if not success:
            print("⚠️ Failed to read frame from camera")
            break
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        # Yield frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video_feed():
    """Video streaming route."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/status')
def status():
    """Health check endpoint."""
    return {
        'status': 'ok',
        'camera': 'connected' if camera and camera.isOpened() else 'disconnected'
    }

@app.route('/')
def index():
    """Simple info page."""
    return """
    <html>
        <head><title>Remote Camera Server</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>🎥 Remote Camera Server</h1>
            <p>Camera is streaming!</p>
            <h2>Video Stream:</h2>
            <img src="/video" style="max-width: 100%; border: 2px solid #333;">
            <h2>Configuration:</h2>
            <p>Use this URL in your pet training app:</p>
            <code style="background: #f0f0f0; padding: 10px; display: block;">
                http://""" + get_local_ip() + """:5000/video
            </code>
        </body>
    </html>
    """

def get_local_ip():
    """Get local IP address."""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("\n" + "="*60)
    print("🎥 Remote Camera Server Starting...")
    print("="*60)
    print(f"\n✅ Camera ready!")
    print(f"\n📺 View stream in browser:")
    print(f"   http://{local_ip}:5000")
    print(f"\n🔗 Use this URL in your pet training app:")
    print(f"   http://{local_ip}:5000/video")
    print(f"\n💡 Make sure both computers are on the same network!")
    print("\n" + "="*60 + "\n")
    
    # Run server
    app.run(host='0.0.0.0', port=5000, threaded=True)
