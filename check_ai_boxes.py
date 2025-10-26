"""
Quick diagnostic to check why AI bounding boxes aren't showing
"""
import requests
import json

print("🔍 Checking AI Detection System...\n")

# Check 1: AI Service
print("1️⃣ Checking AI Service (YOLO8)...")
try:
    response = requests.get("http://localhost:8001/health", timeout=2)
    if response.status_code == 200:
        print("   ✅ AI Service is running")
    else:
        print(f"   ❌ AI Service returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ AI Service not accessible: {e}")
    print("   💡 Start it with: cd ai_service && python main.py")

# Check 2: Backend API
print("\n2️⃣ Checking Backend API...")
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        print("   ✅ Backend API is running")
    else:
        print(f"   ❌ Backend returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend not accessible: {e}")
    print("   💡 Start it with: cd backend && uvicorn app.main:app --reload")

# Check 3: Frame Processor
print("\n3️⃣ Checking Frame Processor...")
try:
    response = requests.get("http://localhost:8000/api/debug/frame-processor-stats", timeout=2)
    if response.status_code == 200:
        stats = response.json()
        print(f"   Running: {stats.get('running', False)}")
        print(f"   Frames processed: {stats.get('frames_processed', 0)}")
        print(f"   Frames dropped: {stats.get('frames_dropped', 0)}")
        print(f"   Queue size: {stats.get('queue_size', 0)}")
        
        if not stats.get('running'):
            print("   ❌ Frame processor is not running!")
        elif stats.get('frames_processed', 0) == 0:
            print("   ⚠️  Frame processor running but no frames processed yet")
        else:
            print("   ✅ Frame processor is working")
    else:
        print(f"   ❌ Could not get stats: {response.status_code}")
except Exception as e:
    print(f"   ❌ Could not check frame processor: {e}")

# Check 4: Video Stream
print("\n4️⃣ Checking Video Stream...")
try:
    response = requests.get("http://localhost:8000/video/mjpeg", timeout=2, stream=True)
    if response.status_code == 200:
        print("   ✅ Video stream is accessible")
    else:
        print(f"   ❌ Video stream returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Video stream not accessible: {e}")

# Check 5: Frontend
print("\n5️⃣ Checking Frontend...")
try:
    response = requests.get("http://localhost:3000", timeout=2)
    if response.status_code == 200:
        print("   ✅ Frontend is running")
    else:
        print(f"   ⚠️  Frontend returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Frontend not accessible: {e}")
    print("   💡 Start it with: cd 'Pet Training Web App' && npm run dev")

print("\n" + "="*60)
print("📋 SUMMARY")
print("="*60)
print("\nFor bounding boxes to show, you need:")
print("1. ✅ AI Service running (port 8001)")
print("2. ✅ Backend running (port 8000)")
print("3. ✅ Frame processor started and processing frames")
print("4. ✅ Frontend running (port 3000)")
print("5. ✅ LivePage using VideoPlayer component (not raw <img>)")
print("6. ✅ WebSocket connection established")
print("7. ✅ AI overlay enabled in UI")

print("\n💡 QUICK FIX:")
print("The LivePage component is showing raw video without the VideoPlayer.")
print("The VideoPlayer has the AIOverlay integrated, but LivePage doesn't use it.")
print("\nYou need to either:")
print("A) Modify LivePage to use VideoPlayer component")
print("B) Add AIOverlay directly to LivePage")
