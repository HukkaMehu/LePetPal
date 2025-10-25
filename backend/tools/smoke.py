import time
import requests
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
PROMPT = sys.argv[2] if len(sys.argv) > 2 else "pick up the ball"

print("health:", requests.get(f"{BASE}/health").json())

# command
r = requests.post(f"{BASE}/command", json={"prompt": PROMPT, "options": {}})
print("command:", r.status_code, r.json())
req_id = r.json().get("request_id")

# poll status
if req_id:
    print("status polling:")
    deadline = time.time() + 6
    while time.time() < deadline:
        s = requests.get(f"{BASE}/status/{req_id}")
        body = s.json()
        print(body)
        if body.get("state") in ("succeeded", "failed", "aborted"):
            break
        time.sleep(0.5)

# dispense and speak
print("dispense:", requests.post(f"{BASE}/dispense_treat", json={"duration_ms": 100}).json())
print("speak:", requests.post(f"{BASE}/speak", json={"text": "Good dog!"}).json())
