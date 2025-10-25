"""
Comprehensive backend feature tests for LePetPal
Run this to verify all backend functionality before connecting frontend
"""

import time
import requests
import sys
from typing import Dict, Any

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_pass(msg: str):
    print(f"{Colors.GREEN}✓ PASS:{Colors.RESET} {msg}")

def print_fail(msg: str):
    print(f"{Colors.RED}✗ FAIL:{Colors.RESET} {msg}")

def print_info(msg: str):
    print(f"{Colors.YELLOW}ℹ INFO:{Colors.RESET} {msg}")

def test_health():
    """Test 1: Health Check"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE}/health", timeout=5)
        data = response.json()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data.get("status") == "ok", f"Expected status=ok, got {data.get('status')}"
        assert "api" in data, "Missing 'api' field"
        assert "version" in data, "Missing 'version' field"
        
        print_pass(f"Backend is healthy: {data}")
        return True
    except Exception as e:
        print_fail(f"Health check failed: {e}")
        return False

def test_video_feed():
    """Test 2: Video Feed"""
    print_test("Video Feed")
    try:
        response = requests.get(f"{BASE}/video_feed", timeout=5, stream=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "multipart/x-mixed-replace" in response.headers.get("Content-Type", ""), \
            f"Expected MJPEG content type, got {response.headers.get('Content-Type')}"
        
        # Read first few bytes to verify stream is working
        chunk = next(response.iter_content(chunk_size=1024))
        assert len(chunk) > 0, "Video stream is empty"
        
        print_pass("Video feed is streaming")
        print_info(f"Content-Type: {response.headers.get('Content-Type')}")
        return True
    except Exception as e:
        print_fail(f"Video feed failed: {e}")
        return False

def test_command_invalid_prompt():
    """Test 3: Invalid Command Rejection"""
    print_test("Invalid Command Rejection")
    try:
        response = requests.post(
            f"{BASE}/command",
            json={"prompt": "invalid command", "options": {}},
            timeout=5
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "error" in data, "Expected error response"
        
        print_pass("Invalid commands are properly rejected")
        print_info(f"Error: {data.get('error', {}).get('message')}")
        return True
    except Exception as e:
        print_fail(f"Invalid command test failed: {e}")
        return False

def test_command_pick_up_ball():
    """Test 4: Pick Up Ball Command"""
    print_test("Pick Up Ball Command")
    try:
        # Send command
        response = requests.post(
            f"{BASE}/command",
            json={"prompt": "pick up the ball", "options": {}},
            timeout=5
        )
        
        assert response.status_code == 202, f"Expected 202, got {response.status_code}"
        data = response.json()
        assert "request_id" in data, "Missing request_id"
        assert data.get("status") == "accepted", f"Expected status=accepted, got {data.get('status')}"
        
        request_id = data["request_id"]
        print_pass(f"Command accepted with request_id: {request_id}")
        
        # Poll status
        print_info("Polling status...")
        phases_seen = []
        max_polls = 30
        poll_count = 0
        
        while poll_count < max_polls:
            time.sleep(0.5)
            status_response = requests.get(f"{BASE}/status/{request_id}", timeout=5)
            status_data = status_response.json()
            
            state = status_data.get("state")
            phase = status_data.get("phase")
            message = status_data.get("message")
            
            if phase and phase not in phases_seen:
                phases_seen.append(phase)
                print_info(f"  Phase: {phase} | State: {state} | Message: {message}")
            
            if state in ("succeeded", "failed", "aborted"):
                print_info(f"  Final state: {state}")
                print_info(f"  Duration: {status_data.get('duration_ms')}ms")
                
                assert state == "succeeded", f"Command failed with state: {state}"
                assert len(phases_seen) > 0, "No phases were executed"
                
                print_pass(f"Command completed successfully through phases: {phases_seen}")
                return True
            
            poll_count += 1
        
        print_fail("Command timed out (no final state after 15 seconds)")
        return False
        
    except Exception as e:
        print_fail(f"Pick up ball command failed: {e}")
        return False

def test_command_busy():
    """Test 5: Busy State Handling"""
    print_test("Busy State Handling")
    try:
        # Start first command
        response1 = requests.post(
            f"{BASE}/command",
            json={"prompt": "pick up the ball", "options": {}},
            timeout=5
        )
        assert response1.status_code == 202, "First command should be accepted"
        
        # Immediately try second command (should be rejected as busy)
        time.sleep(0.2)
        response2 = requests.post(
            f"{BASE}/command",
            json={"prompt": "get the treat", "options": {}},
            timeout=5
        )
        
        if response2.status_code == 409:
            data = response2.json()
            assert "error" in data, "Expected error response"
            assert data["error"]["code"] == "busy", f"Expected busy error, got {data['error']['code']}"
            print_pass("Busy state is properly enforced")
            
            # Wait for first command to complete
            print_info("Waiting for first command to complete...")
            time.sleep(6)
            return True
        else:
            print_fail(f"Expected 409 Busy, got {response2.status_code}")
            return False
            
    except Exception as e:
        print_fail(f"Busy state test failed: {e}")
        return False

def test_go_home():
    """Test 6: Go Home Command (Interrupt)"""
    print_test("Go Home Command (Interrupt)")
    try:
        # Start a command
        response1 = requests.post(
            f"{BASE}/command",
            json={"prompt": "pick up the ball", "options": {}},
            timeout=5
        )
        assert response1.status_code == 202, "First command should be accepted"
        request_id1 = response1.json()["request_id"]
        
        # Immediately send go home (should interrupt)
        time.sleep(0.5)
        response2 = requests.post(
            f"{BASE}/command",
            json={"prompt": "go home", "options": {}},
            timeout=5
        )
        
        assert response2.status_code == 202, f"Go home should be accepted, got {response2.status_code}"
        request_id2 = response2.json()["request_id"]
        
        print_pass("Go home command accepted (should interrupt previous command)")
        
        # Check first command was aborted
        time.sleep(1)
        status1 = requests.get(f"{BASE}/status/{request_id1}", timeout=5).json()
        print_info(f"Previous command state: {status1.get('state')}")
        
        # Wait for go home to complete
        time.sleep(2)
        status2 = requests.get(f"{BASE}/status/{request_id2}", timeout=5).json()
        print_info(f"Go home state: {status2.get('state')}")
        
        print_pass("Go home command completed")
        return True
        
    except Exception as e:
        print_fail(f"Go home test failed: {e}")
        return False

def test_dispense_treat():
    """Test 7: Dispense Treat"""
    print_test("Dispense Treat")
    try:
        response = requests.post(
            f"{BASE}/dispense_treat",
            json={"duration_ms": 600},
            timeout=5
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data.get('status')}"
        
        print_pass("Treat dispensed successfully")
        return True
    except Exception as e:
        print_fail(f"Dispense treat failed: {e}")
        return False

def test_speak():
    """Test 8: Text-to-Speech"""
    print_test("Text-to-Speech")
    try:
        response = requests.post(
            f"{BASE}/speak",
            json={"text": "Good boy!"},
            timeout=5
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data.get('status')}"
        
        print_pass("TTS spoke successfully")
        return True
    except Exception as e:
        print_fail(f"TTS failed: {e}")
        return False

def test_speak_invalid():
    """Test 9: TTS with Empty Text"""
    print_test("TTS with Empty Text")
    try:
        response = requests.post(
            f"{BASE}/speak",
            json={"text": ""},
            timeout=5
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "error" in data, "Expected error response"
        
        print_pass("Empty text is properly rejected")
        return True
    except Exception as e:
        print_fail(f"TTS validation test failed: {e}")
        return False

def test_get_treat_command():
    """Test 10: Get Treat Command"""
    print_test("Get Treat Command")
    try:
        response = requests.post(
            f"{BASE}/command",
            json={"prompt": "get the treat", "options": {}},
            timeout=5
        )
        
        assert response.status_code == 202, f"Expected 202, got {response.status_code}"
        request_id = response.json()["request_id"]
        print_pass(f"Get treat command accepted: {request_id}")
        
        # Wait for completion
        time.sleep(6)
        status = requests.get(f"{BASE}/status/{request_id}", timeout=5).json()
        
        assert status.get("state") == "succeeded", f"Expected succeeded, got {status.get('state')}"
        print_pass("Get treat command completed successfully")
        return True
        
    except Exception as e:
        print_fail(f"Get treat command failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}LePetPal Backend Feature Tests{Colors.RESET}")
    print(f"{Colors.BLUE}Testing backend at: {BASE}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    tests = [
        ("Health Check", test_health),
        ("Video Feed", test_video_feed),
        ("Invalid Command Rejection", test_command_invalid_prompt),
        ("Pick Up Ball Command", test_command_pick_up_ball),
        ("Busy State Handling", test_command_busy),
        ("Go Home (Interrupt)", test_go_home),
        ("Dispense Treat", test_dispense_treat),
        ("Text-to-Speech", test_speak),
        ("TTS Validation", test_speak_invalid),
        ("Get Treat Command", test_get_treat_command),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {name}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    if passed == total:
        print(f"{Colors.GREEN}ALL TESTS PASSED! ({passed}/{total}){Colors.RESET}")
        print(f"{Colors.GREEN}✓ Backend is ready for frontend integration!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}TESTS PASSED: {passed}/{total}{Colors.RESET}")
        print(f"{Colors.RED}TESTS FAILED: {total - passed}/{total}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite crashed: {e}{Colors.RESET}")
        sys.exit(1)
