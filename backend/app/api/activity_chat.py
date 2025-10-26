"""
Activity Chat API
Provides chat interface with visual context from activity log
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
from datetime import datetime
import asyncio
from app.core.config import settings

router = APIRouter(prefix="/activity-chat", tags=["activity-chat"])

# Configuration
# Look for activity log in parent directory (project root)
ACTIVITY_LOG_FILE = Path(__file__).parent.parent.parent.parent / "stream_activity.txt"
OPENAI_API_KEY = settings.OPENAI_API_KEY

# Try to import OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
    if OPENAI_API_KEY:
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        print(f"[ActivityChat] OpenAI client initialized with API key: {OPENAI_API_KEY[:10]}...")
    else:
        openai_client = None
        print("[ActivityChat] OpenAI API key not found")
except ImportError as e:
    print(f"[ActivityChat] Failed to import OpenAI: {e}")
    OPENAI_AVAILABLE = False
    openai_client = None
except Exception as e:
    print(f"[ActivityChat] Error initializing OpenAI client: {e}")
    OPENAI_AVAILABLE = False
    openai_client = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    include_activity_log: bool = True


class ChatResponse(BaseModel):
    response: str
    activity_entries_count: int


class ActivityLogEntry(BaseModel):
    timestamp: str
    description: str


def load_activity_log() -> str:
    """Load activity log from file."""
    if not ACTIVITY_LOG_FILE.exists():
        return ""
    
    try:
        with open(ACTIVITY_LOG_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[ActivityChat] Error loading log: {e}")
        return ""


def parse_activity_log() -> List[ActivityLogEntry]:
    """Parse activity log into structured entries."""
    log_content = load_activity_log()
    if not log_content:
        return []
    
    entries = []
    for line in log_content.strip().split('\n'):
        if not line.strip():
            continue
        
        # Parse format: [2024-10-26 14:30:00] Description
        try:
            if line.startswith('['):
                timestamp_end = line.index(']')
                timestamp = line[1:timestamp_end]
                description = line[timestamp_end + 2:].strip()
                entries.append(ActivityLogEntry(
                    timestamp=timestamp,
                    description=description
                ))
        except Exception:
            continue
    
    return entries


@router.get("/log", response_model=List[ActivityLogEntry])
async def get_activity_log(limit: int = 50):
    """
    Get recent activity log entries.
    
    Args:
        limit: Maximum number of entries to return (most recent)
    """
    entries = parse_activity_log()
    return entries[-limit:] if entries else []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message and get AI response with activity log context.
    
    Args:
        request: Chat request with message and options
    """
    if not OPENAI_AVAILABLE or not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API not available. Set OPENAI_API_KEY environment variable."
        )
    
    # Load activity log
    activity_log = load_activity_log() if request.include_activity_log else ""
    entries_count = len(activity_log.split('\n')) if activity_log else 0
    
    # Build system prompt with activity log context
    if activity_log:
        system_prompt = f"""You are a helpful AI assistant analyzing a pet training video stream. 
You have access to an activity log that describes what has been happening in the video stream.

Activity Log:
{activity_log}

Answer questions about what's happening in the stream based on this activity log. 
Be concise and helpful. If the log doesn't contain relevant information, say so."""
    else:
        system_prompt = """You are a helpful AI assistant for a pet training application. 
The activity log is currently empty - no frames have been captured yet. 
Let the user know they need to wait for the activity logger to capture some frames first."""
    
    try:
        # Call OpenAI API
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        
        return ChatResponse(
            response=answer,
            activity_entries_count=entries_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling OpenAI API: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Send a chat message and stream AI response with activity log context.
    
    Args:
        request: Chat request with message and options
    """
    if not OPENAI_AVAILABLE or not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API not available. Set OPENAI_API_KEY environment variable."
        )
    
    # Load activity log
    activity_log = load_activity_log() if request.include_activity_log else ""
    
    # Build system prompt with activity log context
    if activity_log:
        system_prompt = f"""You are a helpful AI assistant analyzing a pet training video stream. 
You have access to an activity log that describes what has been happening in the video stream.

Activity Log:
{activity_log}

Answer questions about what's happening in the stream based on this activity log. 
Be concise and helpful. If the log doesn't contain relevant information, say so."""
    else:
        system_prompt = """You are a helpful AI assistant for a pet training application. 
The activity log is currently empty - no frames have been captured yet. 
Let the user know they need to wait for the activity logger to capture some frames first."""
    
    async def generate():
        try:
            # Call OpenAI API with streaming
            stream = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.message}
                ],
                max_tokens=500,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"\n\nError: {str(e)}"
    
    return StreamingResponse(generate(), media_type="text/plain")


@router.post("/clear")
async def clear_activity_log():
    """
    Clear the activity log file.
    """
    try:
        if ACTIVITY_LOG_FILE.exists():
            ACTIVITY_LOG_FILE.write_text("")
            return {"success": True, "message": "Activity log cleared"}
        else:
            return {"success": True, "message": "Activity log file does not exist"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing activity log: {str(e)}"
        )


@router.get("/status")
async def get_status():
    """
    Get activity chat system status.
    """
    log_exists = ACTIVITY_LOG_FILE.exists()
    entries_count = 0
    last_entry_time = None
    
    if log_exists:
        entries = parse_activity_log()
        entries_count = len(entries)
        if entries:
            last_entry_time = entries[-1].timestamp
    
    return {
        "openai_available": OPENAI_AVAILABLE and openai_client is not None,
        "openai_client_exists": openai_client is not None,
        "openai_imported": OPENAI_AVAILABLE,
        "api_key_set": bool(OPENAI_API_KEY),
        "api_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "log_file_exists": log_exists,
        "entries_count": entries_count,
        "last_entry_time": last_entry_time,
        "log_file_path": str(ACTIVITY_LOG_FILE.absolute())
    }
