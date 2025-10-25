"""
Simple test script to verify AI service endpoints
Run this after starting the service with: python main.py
"""
import requests
import json
import base64

# Service URL
BASE_URL = "http://localhost:8001"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_vision_process():
    """Test vision processing endpoint"""
    print("Testing vision processing endpoint...")
    
    # Create mock request with fake base64 frame
    payload = {
        "frameBase64": base64.b64encode(b"fake_frame_data").decode(),
        "timestamp": 1234567890.0,
        "enabledModels": ["detector", "pose", "action", "object"]
    }
    
    response = requests.post(f"{BASE_URL}/vision/process", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Detections: {len(data.get('detections', []))}")
        print(f"Keypoints: {len(data.get('keypoints', []))}")
        print(f"Actions: {len(data.get('actions', []))}")
        print(f"Objects: {len(data.get('objects', []))}")
        print(f"Suggested Events: {len(data.get('suggestedEvents', []))}")
        
        # Print sample detection
        if data.get('detections'):
            det = data['detections'][0]
            print(f"\nSample Detection:")
            print(f"  Class: {det['class']}")
            print(f"  Confidence: {det['confidence']}")
            print(f"  Box: {det['box']}")
        
        # Print sample action
        if data.get('actions'):
            action = data['actions'][0]
            print(f"\nTop Action:")
            print(f"  Label: {action['label']}")
            print(f"  Probability: {action['probability']}")
    else:
        print(f"Error: {response.text}")
    
    print()
    return response.status_code == 200


def test_vision_models():
    """Test vision models listing"""
    print("Testing vision models endpoint...")
    response = requests.get(f"{BASE_URL}/vision/models")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Available models: {len(data.get('available', []))}")
        print(f"Active models: {data.get('active', {})}")
    else:
        print(f"Error: {response.text}")
    
    print()
    return response.status_code == 200


def test_coach_tips():
    """Test coach tips endpoint"""
    print("Testing coach tips endpoint...")
    
    payload = {
        "currentAction": "sit",
        "recentEvents": [],
        "sessionContext": {}
    }
    
    response = requests.post(f"{BASE_URL}/coach/tips", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Tip: {data.get('tip')}")
        print(f"Confidence: {data.get('confidence')}")
    else:
        print(f"Error: {response.text}")
    
    print()
    return response.status_code == 200


def test_coach_summary():
    """Test coach summary endpoint"""
    print("Testing coach summary endpoint...")
    
    payload = {
        "sessionStart": "2024-10-24T10:00:00Z",
        "sessionEnd": "2024-10-24T10:30:00Z",
        "events": [],
        "metrics": {
            "sitCount": 12,
            "standCount": 8,
            "lieCount": 5,
            "fetchAttempts": 10,
            "fetchSuccesses": 8,
            "barks": 3,
            "timeInFrameMin": 25
        }
    }
    
    response = requests.post(f"{BASE_URL}/coach/summary", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data.get('summary')}")
        print(f"Wins: {len(data.get('wins', []))}")
        print(f"Setbacks: {len(data.get('setbacks', []))}")
        print(f"Suggestions: {len(data.get('suggestions', []))}")
        print(f"Highlight Clips: {len(data.get('highlightClips', []))}")
    else:
        print(f"Error: {response.text}")
    
    print()
    return response.status_code == 200


def test_coach_chat():
    """Test coach chat endpoint"""
    print("Testing coach chat endpoint...")
    
    payload = {
        "question": "How is my dog's sit training progressing?",
        "context": {
            "events": [],
            "metrics": {}
        }
    }
    
    response = requests.post(f"{BASE_URL}/coach/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data.get('answer')}")
        print(f"Relevant Timestamps: {data.get('relevantTimestamps')}")
    else:
        print(f"Error: {response.text}")
    
    print()
    return response.status_code == 200


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("AI Service Test Suite")
    print("=" * 60)
    print()
    
    results = {
        "Health": test_health(),
        "Vision Process": test_vision_process(),
        "Vision Models": test_vision_models(),
        "Coach Tips": test_coach_tips(),
        "Coach Summary": test_coach_summary(),
        "Coach Chat": test_coach_chat()
    }
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print()
    print(f"Overall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to AI service.")
        print("Make sure the service is running with: python main.py")
    except Exception as e:
        print(f"ERROR: {str(e)}")
