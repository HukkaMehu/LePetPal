"""
Simple test script to verify status API endpoints work correctly.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_get_status():
    """Test GET /api/status endpoint"""
    print("\n=== Testing GET /api/status ===")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify required fields
            assert "device" in data, "Missing 'device' field"
            assert "video" in data, "Missing 'video' field"
            assert "fps" in data, "Missing 'fps' field"
            assert "latencyMs" in data, "Missing 'latencyMs' field"
            assert "aiModels" in data, "Missing 'aiModels' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            
            print("✓ All required fields present")
            
            # Verify device status is valid
            assert data["device"] in ["connected", "offline"], f"Invalid device status: {data['device']}"
            print(f"✓ Device status: {data['device']}")
            
            # Verify video type is valid
            assert data["video"] in ["webrtc", "mjpeg"], f"Invalid video type: {data['video']}"
            print(f"✓ Video type: {data['video']}")
            
            # Verify numeric values
            assert isinstance(data["fps"], (int, float)), "FPS must be numeric"
            assert data["fps"] > 0, "FPS must be positive"
            print(f"✓ FPS: {data['fps']}")
            
            assert isinstance(data["latencyMs"], (int, float)), "Latency must be numeric"
            assert data["latencyMs"] >= 0, "Latency must be non-negative"
            print(f"✓ Latency: {data['latencyMs']}ms")
            
            # Verify AI models structure
            ai_models = data["aiModels"]
            print(f"✓ AI Models: detector={ai_models.get('detector')}, "
                  f"actionRecognizer={ai_models.get('actionRecognizer')}, "
                  f"poseEstimator={ai_models.get('poseEstimator')}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_get_current_telemetry():
    """Test GET /api/telemetry/current endpoint"""
    print("\n=== Testing GET /api/telemetry/current ===")
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry/current")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify required fields
            assert "fps" in data, "Missing 'fps' field"
            assert "latencyMs" in data, "Missing 'latencyMs' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            
            print("✓ All required fields present")
            print(f"✓ FPS: {data['fps']}, Latency: {data['latencyMs']}ms")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_update_telemetry():
    """Test POST /api/telemetry/update endpoint"""
    print("\n=== Testing POST /api/telemetry/update ===")
    try:
        # Update with new telemetry data
        params = {
            "video_type": "webrtc",
            "fps": 60.0,
            "latency_ms": 250.0,
            "temperature": 45.5,
            "battery_level": 85.0
        }
        
        response = requests.post(f"{BASE_URL}/api/telemetry/update", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data.get("success") == True, "Update should succeed"
            print("✓ Telemetry updated successfully")
            
            # Verify the update by fetching current telemetry
            response2 = requests.get(f"{BASE_URL}/api/telemetry/current")
            if response2.status_code == 200:
                current = response2.json()
                assert current["fps"] == 60.0, f"FPS not updated: {current['fps']}"
                assert current["latencyMs"] == 250.0, f"Latency not updated: {current['latencyMs']}"
                print("✓ Telemetry values verified")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Status API Tests")
    print("=" * 60)
    print("\nMake sure the backend server is running on http://localhost:8000")
    print("and the AI service is running on http://localhost:8001")
    
    results = []
    
    # Run tests
    results.append(("GET /api/status", test_get_status()))
    results.append(("GET /api/telemetry/current", test_get_current_telemetry()))
    results.append(("POST /api/telemetry/update", test_update_telemetry()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
