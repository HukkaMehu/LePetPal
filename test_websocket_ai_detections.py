"""
Test WebSocket AI detections
Connect to WebSocket and listen for ai_detections messages
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/ui"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket")
            
            # Wait for messages
            print("\nListening for messages (press Ctrl+C to stop)...")
            print("-" * 60)
            
            message_count = 0
            ai_detection_count = 0
            
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    msg_type = data.get("type", "unknown")
                    
                    if msg_type == "ai_detections":
                        ai_detection_count += 1
                        detections = data.get("data", {}).get("detections", [])
                        print(f"\n[{ai_detection_count}] AI Detection received:")
                        print(f"  Timestamp: {data.get('timestamp')}")
                        print(f"  Detections: {len(detections)}")
                        for det in detections:
                            print(f"    - {det.get('class_name')}: {det.get('confidence'):.2f}")
                    else:
                        print(f"[{message_count}] Message type: {msg_type}")
                    
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
                    
    except websockets.exceptions.WebSocketException as e:
        print(f"✗ WebSocket error: {e}")
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
