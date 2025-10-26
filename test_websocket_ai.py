"""
Test if AI detections are being broadcast via WebSocket
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/ui"
    
    print(f"🔌 Connecting to WebSocket: {uri}")
    print("Waiting for AI detection messages...\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Listening for messages...\n")
            
            message_count = 0
            ai_detection_count = 0
            
            # Listen for 10 seconds
            timeout = 10
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message_count += 1
                    
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    print(f"📨 Message {message_count}: type='{msg_type}'")
                    
                    if msg_type == 'ai_detections':
                        ai_detection_count += 1
                        detections = data.get('data', {}).get('detections', [])
                        print(f"   🎯 AI Detections: {len(detections)} objects")
                        for det in detections[:3]:  # Show first 3
                            print(f"      - {det.get('class')}: {det.get('confidence'):.2f}")
                    
                except asyncio.TimeoutError:
                    continue
            
            print(f"\n📊 Summary:")
            print(f"   Total messages: {message_count}")
            print(f"   AI detection messages: {ai_detection_count}")
            
            if ai_detection_count == 0:
                print("\n❌ No AI detection messages received!")
                print("   The frame processor is not broadcasting AI results.")
                print("   Check backend logs for [FrameProcessor] errors.")
            else:
                print("\n✅ AI detections are being broadcast!")
                print("   If you don't see boxes in frontend, check:")
                print("   1. Frontend WebSocket connection")
                print("   2. AIOverlay component is receiving messages")
                print("   3. Browser console for errors")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_websocket())
