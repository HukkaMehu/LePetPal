"""
Diagnose why frontend isn't showing video
"""
import httpx
import asyncio

async def check_all():
    print("🔍 Diagnosing frontend video issue...\n")
    
    # 1. Check if backend is running
    print("1️⃣ Checking if backend is running...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("   ✅ Backend is running\n")
            else:
                print(f"   ❌ Backend returned status {response.status_code}\n")
                return
    except httpx.ConnectError:
        print("   ❌ Backend is NOT running!")
        print("   Start it with: cd backend && python -m uvicorn app.main:app --reload\n")
        return
    
    # 2. Check if remote_video endpoint exists
    print("2️⃣ Checking if remote_video endpoint is registered...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/api/remote-video/test?url=https://lepetpal.verkkoventure.com/camera")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint exists: {data.get('status')}\n")
            else:
                print(f"   ❌ Endpoint returned status {response.status_code}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # 3. Check if the stream endpoint works
    print("3️⃣ Checking if stream endpoint works...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "http://localhost:8000/api/remote-video/stream?url=https://lepetpal.verkkoventure.com/camera"
            print(f"   Testing: {url}")
            
            async with client.stream('GET', url) as response:
                if response.status_code == 200:
                    print(f"   ✅ Stream endpoint is working!")
                    print(f"   Content-Type: {response.headers.get('content-type')}")
                    
                    # Read first chunk
                    chunk_count = 0
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            chunk_count += 1
                            if chunk_count >= 3:
                                break
                    
                    print(f"   ✅ Received {chunk_count} chunks\n")
                else:
                    print(f"   ❌ Status: {response.status_code}\n")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
    
    # 4. Check frontend .env
    print("4️⃣ Checking frontend .env configuration...")
    try:
        with open("Pet Training Web App/.env", "r") as f:
            content = f.read()
            if "remote-video/stream" in content:
                print("   ✅ Frontend .env has remote-video endpoint")
                # Extract the URL
                for line in content.split('\n'):
                    if 'VITE_VIDEO_STREAM_URL' in line:
                        print(f"   {line}")
            else:
                print("   ⚠️  Frontend .env might not be configured correctly")
    except Exception as e:
        print(f"   ❌ Error reading .env: {e}")
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Make sure backend is running: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Restart frontend dev server: cd 'Pet Training Web App' && npm run dev")
    print("3. Open http://localhost:3000 in browser")
    print("4. Open DevTools (F12) and check Console for errors")
    print("5. Look for the video stream URL being requested")

asyncio.run(check_all())
