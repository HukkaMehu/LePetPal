"""
WebSocket connection manager for real-time event broadcasting.
Supports multiple clients and Redis pub/sub for multi-instance deployments.
"""
import json
import asyncio
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # Active WebSocket connections
        self.active_connections: Set[WebSocket] = set()
        # Redis client for pub/sub
        self.redis: Optional[Redis] = None
        # Redis pubsub instance
        self.pubsub = None
        # Background task for Redis subscription
        self.redis_task: Optional[asyncio.Task] = None
        # Channel name for Redis pub/sub
        self.channel = "dogmonitor:events"
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSocket clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
            
    async def broadcast_event(self, event_type: str, data: Any):
        """Broadcast an event message to all clients."""
        message = {
            "type": "event",
            "event_type": event_type,
            "data": data
        }
        await self.broadcast(message)
        
        # Also publish to Redis for multi-instance support
        if self.redis:
            await self.publish_to_redis(message)
            
    async def broadcast_overlay(self, overlay_type: str, data: Any):
        """Broadcast overlay data to all clients."""
        message = {
            "type": "overlay",
            "overlay_type": overlay_type,
            "data": data
        }
        await self.broadcast(message)
        
        # Also publish to Redis for multi-instance support
        if self.redis:
            await self.publish_to_redis(message)
            
    async def broadcast_telemetry(self, data: Any):
        """Broadcast telemetry data to all clients."""
        message = {
            "type": "telemetry",
            "data": data
        }
        await self.broadcast(message)
        
        # Also publish to Redis for multi-instance support
        if self.redis:
            await self.publish_to_redis(message)
            
    async def publish_to_redis(self, message: Dict[str, Any]):
        """Publish a message to Redis pub/sub channel."""
        try:
            if self.redis:
                await self.redis.publish(
                    self.channel,
                    json.dumps(message)
                )
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")
            
    async def setup_redis(self, redis_url: str):
        """Initialize Redis connection and start subscription listener."""
        try:
            self.redis = Redis.from_url(redis_url, decode_responses=True)
            # Test connection
            await self.redis.ping()
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(self.channel)
            
            # Start background task to listen for Redis messages
            self.redis_task = asyncio.create_task(self._redis_listener())
            logger.info("Redis pub/sub initialized successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}. WebSocket will work in single-instance mode.")
            self.redis = None
            self.pubsub = None
            
    async def _redis_listener(self):
        """Background task that listens for Redis pub/sub messages."""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        # Broadcast to local WebSocket connections
                        await self.broadcast(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding Redis message: {e}")
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
            
    async def shutdown(self):
        """Clean up resources on shutdown."""
        # Cancel Redis listener task
        if self.redis_task:
            self.redis_task.cancel()
            try:
                await self.redis_task
            except asyncio.CancelledError:
                pass
                
        # Close Redis connections
        if self.pubsub:
            try:
                await self.pubsub.unsubscribe(self.channel)
                await self.pubsub.close()
            except Exception as e:
                logger.warning(f"Error closing pubsub: {e}")
            
        if self.redis:
            try:
                await self.redis.close()
            except Exception as e:
                logger.warning(f"Error closing redis: {e}")
            
        # Close all WebSocket connections
        for connection in list(self.active_connections):
            try:
                await connection.close()
            except Exception:
                pass
        self.active_connections.clear()
        
        logger.info("ConnectionManager shutdown complete")


# Global connection manager instance
manager = ConnectionManager()
