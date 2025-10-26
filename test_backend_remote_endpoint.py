"""
Test the backend's remote video endpoint
"""
import httpx
import asyncio

async def test_backend_endpoint():
    # Test the backend endpoint
    backend_url = "http://localhost:8000/api/remote-video/stream"
    camera_url = "https://lepetpal.verkkoventure.com/camera"
    
    full_url = f"{backend_url}?url={camera_url}"
    
    print(f"Testing backend endpoint: {full_url}")
    print("This should proxy the remote camera through your backend...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream('GET', full_url) as response:
                print(f"Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type')}")
                
                if response.status_code == 200:
                    print("\n✅ Backend endpoint is working!")
                    print("Reading first few chunks...\n")
                    
                    chunk_count = 0
                    async for chunk in response.aiter_bytes():
                        chunk_count += 1
                        print(f"Chunk {chunk_count}: {len(chunk)} bytes")
                        if chunk_count >= 5:
                            break
                    
                    print(f"\n✅ Successfully received {chunk_count} chunks from backend!")
                    print("The remote video endpoint is working correctly.")
                else:
                    print(f"\n❌ Error: Status code {response.status_code}")
                    text = await response.aread()
                    print(f"Response: {text.decode()}")
                    
        except httpx.ConnectError:
            print("❌ Connection error - is the backend running on localhost:8000?")
        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_backend_endpoint())
