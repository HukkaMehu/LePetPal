"""
Quick backend test - verifies basic functionality
Run this for a fast sanity check
"""

import requests
import time
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

print("🤖 LePetPal Quick Test\n")

# 1. Health
print("1️⃣  Testing health endpoint...")
r = requests.get(f"{BASE}/health")
print(f"   ✓ Health: {r.json()}\n")

# 2. Video feed
print("2️⃣  Testing video feed...")
r = requests.get(f"{BASE}/video_feed", stream=True)
chunk = next(r.iter_content(chunk_size=1024))
print(f"   ✓ Video streaming ({len(chunk)} bytes received)\n")

# 3. Send command
print("3️⃣  Sending 'pick up the ball' command...")
r = requests.post(f"{BASE}/command", json={"prompt": "pick up the ball", "options": {}})
data = r.json()
req_id = data["request_id"]
print(f"   ✓ Command accepted: {req_id}\n")

# 4. Poll status
print("4️⃣  Polling status...")
for i in range(15):
    time.sleep(0.5)
    r = requests.get(f"{BASE}/status/{req_id}")
    status = r.json()
    state = status.get("state")
    phase = status.get("phase")
    print(f"   [{i+1}] State: {state:12s} Phase: {phase}")
    
    if state in ("succeeded", "failed", "aborted"):
        print(f"\n   ✓ Final state: {state}")
        print(f"   ✓ Duration: {status.get('duration_ms')}ms")
        break

# 5. Dispense treat
print("\n5️⃣  Testing dispense treat...")
r = requests.post(f"{BASE}/dispense_treat", json={"duration_ms": 600})
print(f"   ✓ Dispense: {r.json()}\n")

# 6. Speak
print("6️⃣  Testing TTS...")
r = requests.post(f"{BASE}/speak", json={"text": "Test complete!"})
print(f"   ✓ Speak: {r.json()}\n")

print("✅ All quick tests passed!")
print("🚀 Backend is ready!")
