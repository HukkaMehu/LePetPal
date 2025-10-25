from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.websocket import manager
from app.api import video, websocket, events, snapshots, clips, analytics, routines, commands, models, status
from app.workers.event_processor import event_processor
from app.workers.metrics_aggregator import metrics_aggregator
from app.workers.routine_scheduler import routine_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Initialize Redis for WebSocket pub/sub
    await manager.setup_redis(settings.REDIS_URL)
    # Startup: Start event processor
    await event_processor.start()
    # Startup: Start metrics aggregator
    await metrics_aggregator.start()
    # Startup: Start routine scheduler
    await routine_scheduler.start()
    yield
    # Shutdown: Clean up resources
    await event_processor.stop()
    await metrics_aggregator.stop()
    await routine_scheduler.stop()
    await manager.shutdown()
    # Shutdown: Release webcam
    video.cleanup_webcam()


app = FastAPI(
    title="Dog Monitor API",
    description="Backend API for dog monitoring and training assistant",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video.router)
app.include_router(websocket.router)
app.include_router(events.router)
app.include_router(snapshots.router)
app.include_router(clips.router)
app.include_router(analytics.router)
app.include_router(routines.router)
app.include_router(commands.router)
app.include_router(models.router)
app.include_router(status.router)

@app.get("/")
async def root():
    return {"message": "Dog Monitor API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
