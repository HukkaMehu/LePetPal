"""
Test direct access to the remote camera
"""
import httpx
import asyncio

async def test_camera():
    camera_url = "https://lepetpal.verkkoventure.com/camera"
    
    print(f"Testing direct access to: {camera_url}")
    print("Attempting to fetch first few bytes...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream('GET', camera_url) as response:
                print(f"✅ Status: {response.status_code}")
                print(f"✅ Content-Type: {response.headers.get('content-type')}")
                print(f"✅ Headers: {dict(response.headers)}\n")
                
                if response.status_code == 200:
                    print("Reading first chunk of data...")
                    chunk_count = 0
                    async for chunk in response.aiter_bytes():
                        chunk_count += 1
                        print(f"Chunk {chunk_count}: {len(chunk)} bytes")
                        if chunk_count >= 3:
                            break
                    print(f"\n✅ Successfully received {chunk_count} chunks from camera!")
                else:
                    print(f"❌ Error: Unexpected status code {response.status_code}")
                    
        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_camera())
