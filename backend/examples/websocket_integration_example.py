"""
Example showing how to integrate WebSocket broadcasting with AI detection pipeline.
This demonstrates how the AI service would send detections to WebSocket clients.
"""
import asyncio
from datetime import datetime
from app.core.events import (
    broadcast_dog_detection,
    broadcast_action,
    broadcast_overlay_update,
    broadcast_telemetry
)


async def simulate_ai_detection_pipeline():
    """
    Simulates an AI detection pipeline that processes video frames
    and broadcasts results to WebSocket clients.
    """
    
    # Simulate processing a video frame
    print("Processing frame...")
    
    # 1. Dog detection result
    detection = {
        "box": {"x": 150, "y": 200, "w": 300, "h": 400},
        "confidence": 0.95,
        "class": "dog"
    }
    await broadcast_dog_detection(detection)
    print("✓ Broadcasted dog detection")
    
    # 2. Broadcast overlay data for rendering bounding boxes
    overlay_data = {
        "boxes": [
            {
                "x": 150,
                "y": 200,
                "w": 300,
                "h": 400,
                "label": "dog",
                "confidence": 0.95
            }
        ]
    }
    await broadcast_overlay_update("detection", overlay_data)
    print("✓ Broadcasted detection overlay")
    
    # 3. Action recognition result
    await broadcast_action("sit", confidence=0.92, metadata={
        "duration": 3.5,
        "timestamp": datetime.utcnow().isoformat()
    })
    print("✓ Broadcasted sit action")
    
    # 4. Pose estimation overlay
    pose_data = {
        "keypoints": [
            {"name": "nose", "x": 300, "y": 250, "confidence": 0.98},
            {"name": "left_shoulder", "x": 280, "y": 320, "confidence": 0.95},
            {"name": "right_shoulder", "x": 320, "y": 320, "confidence": 0.94},
            {"name": "spine", "x": 300, "y": 380, "confidence": 0.96}
        ]
    }
    await broadcast_overlay_update("pose", pose_data)
    print("✓ Broadcasted pose overlay")
    
    # 5. System telemetry
    telemetry = {
        "fps": 30,
        "latency_ms": 85,
        "gpu_temp": 62.5,
        "cpu_usage": 45.2,
        "memory_usage": 2048
    }
    await broadcast_telemetry(telemetry)
    print("✓ Broadcasted telemetry")


async def simulate_continuous_monitoring():
    """
    Simulates continuous monitoring with periodic updates.
    This would run in a background task in the real application.
    """
    print("\nStarting continuous monitoring simulation...")
    print("(This would run continuously in production)\n")
    
    for i in range(3):
        print(f"\n--- Frame {i+1} ---")
        await simulate_ai_detection_pipeline()
        await asyncio.sleep(2)  # Simulate frame processing time
    
    print("\n✓ Simulation complete")


# Example of how to integrate with FastAPI background tasks
async def start_ai_monitoring_task():
    """
    This function would be called as a background task when the server starts.
    It continuously processes video frames and broadcasts results.
    """
    while True:
        try:
            # Get frame from video source
            # frame = await get_video_frame()
            
            # Process with AI models
            # detections = await ai_service.detect(frame)
            # actions = await ai_service.recognize_actions(frame)
            # pose = await ai_service.estimate_pose(frame)
            
            # Broadcast results
            # await broadcast_dog_detection(detections)
            # await broadcast_overlay_update("detection", detections)
            # await broadcast_action(actions[0]["label"], actions[0]["confidence"])
            # await broadcast_overlay_update("pose", pose)
            
            # Simulate frame processing
            await asyncio.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            print(f"Error in AI monitoring: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    # Run the simulation
    asyncio.run(simulate_continuous_monitoring())
