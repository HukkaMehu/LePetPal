"""
Quick test script to verify video endpoints are working
"""
import requests
import time

BACKEND_URL = "http://localhost:8000"

def test_mjpeg_endpoint():
    """Test if MJPEG endpoint is accessible"""
    print("\n=== Testing MJPEG Endpoint ===")
    url = f"{BACKEND_URL}/video/mjpeg?webcam=true"
    print(f"Testing: {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            # Read first few bytes to verify stream is working
            chunk = next(response.iter_content(chunk_size=1024))
            print(f"✓ Stream is working! Received {len(chunk)} bytes")
            print(f"✓ First bytes: {chunk[:50]}")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed - is the backend running on {BACKEND_URL}?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_webrtc_offer():
    """Test if WebRTC offer endpoint is accessible"""
    print("\n=== Testing WebRTC Offer Endpoint ===")
    url = f"{BACKEND_URL}/video/webrtc/offer?webcam=true"
    print(f"Testing: {url}")
    
    # Simple SDP offer for testing
    test_offer = {
        "sdp": "v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n",
        "type": "offer"
    }
    
    try:
        response = requests.post(url, json=test_offer, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ WebRTC endpoint is working!")
            print(f"✓ Received answer with SDP type: {data.get('type')}")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed - is the backend running on {BACKEND_URL}?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_api_health():
    """Test if backend API is responding"""
    print("\n=== Testing Backend Health ===")
    url = f"{BACKEND_URL}/api/health"
    print(f"Testing: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ Backend is healthy!")
            return True
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed - is the backend running on {BACKEND_URL}?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Video Endpoint Test Script")
    print("=" * 60)
    
    # Test backend health first
    health_ok = test_api_health()
    
    if not health_ok:
        print("\n⚠ Backend health check failed. Make sure backend is running:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
        exit(1)
    
    # Test video endpoints
    mjpeg_ok = test_mjpeg_endpoint()
    webrtc_ok = test_webrtc_offer()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Backend Health: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"MJPEG Stream:   {'✓ PASS' if mjpeg_ok else '✗ FAIL'}")
    print(f"WebRTC Offer:   {'✓ PASS' if webrtc_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if mjpeg_ok:
        print(f"\n✓ Video streaming is working!")
        print(f"  Open in browser: {BACKEND_URL}/video/mjpeg?webcam=true")
    else:
        print(f"\n✗ Video streaming has issues. Check backend logs.")
