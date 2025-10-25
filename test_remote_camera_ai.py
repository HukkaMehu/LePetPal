"""
Test Remote Camera with AI
Quick test to verify remote camera works with AI processing
"""
import asyncio
import httpx

REMOTE_CAMERA_URL = "https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed"
BACKEND_URL = "http://localhost:8000"


async def test_remote_camera_ai():
    """Test remote camera integration with AI"""
    print("=" * 60)
    print("Testing Remote Camera with AI")
    print("=" * 60)
    print()
    
    # Test 1: Check remote camera is accessible
    print("1. Testing remote camera connection...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(REMOTE_CAMERA_URL, timeout=10.0)
            if response.status_code == 200:
                print(f"   ✓ Remote camera is accessible")
                print(f"   - URL: {REMOTE_CAMERA_URL}")
                print(f"   - Content-Type: {response.headers.get('content-type')}")
            else:
                print(f"   ✗ Remote camera returned status {response.status_code}")
                print("   → Check if remote_camera_server.py is running")
                print("   → Check if ngrok tunnel is active")
                return
    except Exception as e:
        print(f"   ✗ Cannot reach remote camera: {e}")
        print("   → Check if remote_camera_server.py is running")
        print("   → Check if ngrok tunnel is active")
        return
    
    # Test 2: Check backend is running
    print("\n2. Testing backend...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("   ✓ Backend is running")
            else:
                print(f"   ✗ Backend returned status {response.status_code}")
                return
    except Exception as e:
        print(f"   ✗ Backend not reachable: {e}")
        print("   → Start backend: cd backend && python -m uvicorn app.main:app --reload")
        return
    
    # Test 3: Check AI service
    print("\n3. Testing AI service...")
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
    
    # Test 4: Check frame processor
    print("\n4. Testing frame processor...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/debug/frame-processor-stats",
                timeout=5.0
            )
            if response.status_code == 200:
                stats = response.json()
                print(f"   ✓ Frame processor running: {stats['running']}")
                print(f"   - Frames processed: {stats['frames_processed']}")
                print(f"   - Frames dropped: {stats['frames_dropped']}")
            else:
                print(f"   ✗ Could not get stats: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error getting stats: {e}")
    
    # Test 5: Test remote video proxy endpoint
    print("\n5. Testing remote video proxy...")
    try:
        async with httpx.AsyncClient() as client:
            test_url = f"{BACKEND_URL}/remote-video/test?url={REMOTE_CAMERA_URL}"
            response = await client.get(test_url, timeout=10.0)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'connected':
                    print("   ✓ Remote video proxy working")
                    print(f"   - Status: {result['status']}")
                    print(f"   - Message: {result['message']}")
                else:
                    print(f"   ✗ Connection failed: {result.get('message')}")
            else:
                print(f"   ✗ Proxy test failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing proxy: {e}")
    
    # Test 6: Show stream URL
    print("\n6. Stream URLs:")
    print(f"   📺 Direct remote camera:")
    print(f"      {REMOTE_CAMERA_URL}")
    print()
    print(f"   🤖 Remote camera with AI:")
    print(f"      {BACKEND_URL}/remote-video/stream?url={REMOTE_CAMERA_URL}&ai=true")
    print()
    print(f"   🎥 Remote camera without AI:")
    print(f"      {BACKEND_URL}/remote-video/stream?url={REMOTE_CAMERA_URL}&ai=false")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open browser to test stream:")
    print(f"   {BACKEND_URL}/remote-video/stream?url={REMOTE_CAMERA_URL}&ai=true")
    print()
    print("2. Update frontend VideoPlayer to use:")
    print(f"   const videoUrl = '{BACKEND_URL}/remote-video/stream?url={REMOTE_CAMERA_URL}&ai=true';")
    print()
    print("3. Check browser console (F12) for 'ai_detections' messages")
    print()
    print("4. Watch Event Feed for AI-generated events")
    print()


if __name__ == "__main__":
    asyncio.run(test_remote_camera_ai())
