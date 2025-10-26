"""
Check if the AI pipeline is working
"""
import httpx
import asyncio

async def check_pipeline():
    print("🔍 Checking AI Pipeline...\n")
    
    # 1. Check if AI service is running
    print("1️⃣ Checking AI service...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                print("   ✅ AI service is running\n")
            else:
                print(f"   ❌ AI service returned status {response.status_code}\n")
                return
    except httpx.ConnectError:
        print("   ❌ AI service is NOT running!")
        print("   Start it with: cd ai_service && python main.py\n")
        return
    
    # 2. Check frame processor stats
    print("2️⃣ Checking frame processor stats...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/api/debug/frame-processor-stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"   Running: {stats.get('running')}")
                print(f"   Frames processed: {stats.get('frames_processed')}")
                print(f"   Frames dropped: {stats.get('frames_dropped')}")
                print(f"   Queue size: {stats.get('queue_size')}\n")
                
                if stats.get('frames_processed', 0) == 0:
                    print("   ⚠️  No frames have been processed yet!")
                    print("   This means frames aren't reaching the AI service.\n")
                else:
                    print("   ✅ Frames are being processed!\n")
            else:
                print(f"   ❌ Status: {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # 3. Test AI service directly
    print("3️⃣ Testing AI service with a test frame...")
    try:
        import base64
        import cv2
        import numpy as np
        
        # Create a simple test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_frame, "TEST", (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        _, buffer = cv2.imencode('.jpg', test_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://localhost:8001/vision/process",
                json={
                    "frameBase64": frame_base64,
                    "timestamp": 0,
                    "enabledModels": ["detector"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ AI service responded successfully")
                print(f"   Detections: {len(result.get('detections', []))}")
                print(f"   Response: {result}\n")
            else:
                print(f"   ❌ AI service returned status {response.status_code}\n")
                
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("📋 DIAGNOSIS:")
    print("="*60)
    print("If frames_processed is 0:")
    print("  - Check that remote_video.py is calling frame_processor.submit_frame()")
    print("  - Check backend logs for [FrameProcessor] messages")
    print("  - Make sure AI service URL is correct in backend/.env")
    print("\nIf AI service test works but frames_processed is still 0:")
    print("  - The issue is in remote_video.py not submitting frames")
    print("  - Check if process_ai parameter is True")

asyncio.run(check_pipeline())
