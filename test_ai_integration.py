"""
Test AI Integration
Quick script to verify AI features are working
"""
import asyncio
import httpx
import base64
import cv2
import numpy as np


async def test_ai_service():
    """Test AI service is running and processing frames"""
    print("=" * 50)
    print("Testing AI Integration")
    print("=" * 50)
    print()
    
    # Test 1: Check AI service health
    print("1. Checking AI service health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            if response.status_code == 200:
                print("   ✓ AI service is running")
            else:
                print(f"   ✗ AI service returned status {response.status_code}")
                return
    except Exception as e:
        print(f"   ✗ AI service not reachable: {e}")
        print("   → Start AI service: cd ai_service && python main.py")
        return
    
    # Test 2: Check backend health
    print("\n2. Checking backend health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                print("   ✓ Backend is running")
            else:
                print(f"   ✗ Backend returned status {response.status_code}")
                return
    except Exception as e:
        print(f"   ✗ Backend not reachable: {e}")
        print("   → Start backend: cd backend && python -m uvicorn app.main:app --reload")
        return
    
    # Test 3: Check frame processor stats
    print("\n3. Checking frame processor...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/debug/frame-processor-stats", timeout=5.0)
            if response.status_code == 200:
                stats = response.json()
                print(f"   ✓ Frame processor running: {stats['running']}")
                print(f"   - Frames processed: {stats['frames_processed']}")
                print(f"   - Frames dropped: {stats['frames_dropped']}")
                print(f"   - Queue size: {stats['queue_size']}")
            else:
                print(f"   ✗ Could not get stats: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error getting stats: {e}")
    
    # Test 4: Test AI vision processing with a test frame
    print("\n4. Testing AI vision processing...")
    try:
        # Create a test frame (solid color)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:] = (100, 150, 200)  # BGR color
        
        # Add some text
        cv2.putText(test_frame, "TEST FRAME", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', test_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send to AI service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/vision/process",
                json={
                    "frameBase64": frame_base64,
                    "timestamp": 0,
                    "enabledModels": ["detector", "pose", "action", "object"]
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✓ AI processing successful")
                print(f"   - Detections: {len(result.get('detections', []))}")
                print(f"   - Actions: {len(result.get('actions', []))}")
                print(f"   - Objects: {len(result.get('objects', []))}")
                print(f"   - Suggested events: {len(result.get('suggestedEvents', []))}")
                
                # Show first detection if any
                if result.get('detections'):
                    det = result['detections'][0]
                    print(f"\n   First detection:")
                    print(f"   - Class: {det['class_name']}")
                    print(f"   - Confidence: {det['confidence']}")
            else:
                print(f"   ✗ AI processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error testing AI: {e}")
    
    # Test 5: Check if YOLOv8 is loaded
    print("\n5. Checking YOLOv8 model...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/vision/models", timeout=5.0)
            if response.status_code == 200:
                models = response.json()
                print("   ✓ Models endpoint accessible")
                print(f"   - Available models: {len(models.get('available', []))}")
            else:
                print(f"   ✗ Could not get models: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error getting models: {e}")
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Go to Live page")
    print("3. Check browser console for 'ai_detections' messages")
    print("4. Watch Event Feed for AI-generated events")
    print()


if __name__ == "__main__":
    asyncio.run(test_ai_service())
