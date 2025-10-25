"""
WebSocket API endpoints for real-time event streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/ui")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for UI clients to receive real-time events, overlays, and telemetry.
    
    Message format:
    {
        "type": "event" | "overlay" | "telemetry",
        "event_type": str (for events),
        "overlay_type": str (for overlays),
        "data": any
    }
    """
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "message": "WebSocket connection established"
            },
            websocket
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (for future bidirectional communication)
            data = await websocket.receive_json()
            
            # Echo back for now (can be extended for client commands)
            logger.info(f"Received message from client: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
