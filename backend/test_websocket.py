"""
Simple test script to verify WebSocket functionality.
Run the FastAPI server first, then run this script.
"""
import asyncio
import json
from websockets import connect


async def test_websocket():
    """Test WebSocket connection and message receiving."""
    uri = "ws://localhost:8000/ws/ui"
    
    try:
        async with connect(uri) as websocket:
            print("✓ Connected to WebSocket")
            
            # Receive connection confirmation
            message = await websocket.recv()
            data = json.loads(message)
            print(f"✓ Received: {data}")
            
            # Send a test message
            test_msg = {"type": "ping", "message": "Hello from test client"}
            await websocket.send(json.dumps(test_msg))
            print(f"✓ Sent: {test_msg}")
            
            # Keep connection alive for a few seconds to test
            print("Waiting for messages (5 seconds)...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✓ Received: {json.loads(message)}")
            except asyncio.TimeoutError:
                print("✓ No messages received (expected)")
            
            print("✓ Test completed successfully")
            
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
