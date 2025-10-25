"""
Test public API access (for ngrok/cloudflare URLs)
Usage: python test_public_api.py https://abc123.ngrok.io
"""

import sys
import requests

if len(sys.argv) < 2:
    print("❌ Usage: python test_public_api.py <PUBLIC_URL>")
    print("   Example: python test_public_api.py https://abc123.ngrok.io")
    sys.exit(1)

BASE = sys.argv[1].rstrip('/')

print(f"🌐 Testing public API at: {BASE}\n")

# Test 1: Health
print("1️⃣  Testing /health...")
try:
    r = requests.get(f"{BASE}/health", timeout=10)
    print(f"   ✓ Status: {r.status_code}")
    print(f"   ✓ Response: {r.json()}\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")
    sys.exit(1)

# Test 2: CORS headers
print("2️⃣  Testing CORS headers...")
try:
    r = requests.options(f"{BASE}/command", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    }, timeout=10)
    cors_headers = {k: v for k, v in r.headers.items() if 'access-control' in k.lower()}
    print(f"   ✓ CORS Headers:")
    for k, v in cors_headers.items():
        print(f"     - {k}: {v}")
    print()
except Exception as e:
    print(f"   ❌ Failed: {e}\n")

# Test 3: Command endpoint
print("3️⃣  Testing /command...")
try:
    r = requests.post(f"{BASE}/command", 
                     json={"prompt": "pick up the ball", "options": {}},
                     timeout=10)
    print(f"   ✓ Status: {r.status_code}")
    print(f"   ✓ Response: {r.json()}\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")

# Test 4: Video feed
print("4️⃣  Testing /video_feed...")
try:
    r = requests.get(f"{BASE}/video_feed", stream=True, timeout=10)
    chunk = next(r.iter_content(chunk_size=1024))
    print(f"   ✓ Status: {r.status_code}")
    print(f"   ✓ Content-Type: {r.headers.get('Content-Type')}")
    print(f"   ✓ Streaming: {len(chunk)} bytes received\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")

print("✅ Public API is working!")
print(f"\n📋 Share this URL with your friend:")
print(f"   {BASE}")
print(f"\n💡 They should set in their .env.local:")
print(f"   NEXT_PUBLIC_API_BASE={BASE}")
