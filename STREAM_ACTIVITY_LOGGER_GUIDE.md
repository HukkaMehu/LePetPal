# Stream Activity Logger Guide

Capture frames from your video stream and log activity descriptions using AI vision models. Then chat with the log to ask questions about what happened.

## Quick Start

### 1. Install Dependencies

```bash
pip install opencv-python openai pillow python-dotenv
# OR for Gemini:
pip install opencv-python google-generativeai pillow python-dotenv
```

### 2. Configure Settings

Edit `.env.logger` file and add your API key:

```bash
# OpenAI (recommended)
OPENAI_API_KEY=sk-your-actual-key-here

# Or Gemini
# GEMINI_API_KEY=your-gemini-key-here

# Video source (0 for webcam, or URL)
VIDEO_SOURCE=0

# Capture interval in seconds
CAPTURE_INTERVAL=15
```

### 3. Start Logging Activity

**Easy way (Windows):**
```bash
start_activity_logger.bat
```

**Command line:**

```bash
# Uses settings from .env.logger
python stream_activity_logger.py

# Or override settings
python stream_activity_logger.py --source http://192.168.1.100:5000/video --interval 30
```

### 4. Chat with the Log

**Easy way (Windows):**
```bash
start_chat.bat
```

**Command line:**
```bash
python chat_with_activity_log.py
```

Then ask questions like:
- "What happened between 2pm and 3pm?"
- "Did my dog do anything interesting?"
- "Was there any movement in the last hour?"
- "Summarize the activity today"

## Options

### Stream Activity Logger

```bash
python stream_activity_logger.py \
  --source 0                          # Video source (URL or camera index)
  --log stream_activity.txt           # Log file path
  --interval 10                       # Seconds between captures
  --provider openai                   # "openai" or "gemini"
  --model gpt-4o-mini                 # Optional: specific model
```

### Chat with Log

```bash
python chat_with_activity_log.py \
  --log stream_activity.txt           # Log file to analyze
  --provider openai                   # "openai" or "gemini"
  --question "What happened today?"   # Single question (non-interactive)
```

## Cost Optimization

**OpenAI (Recommended):**
- Uses `gpt-4o-mini` by default (~$0.00015 per image)
- Images resized to 800px width
- Low detail mode enabled
- ~$0.54 per hour at 10s intervals

**Gemini:**
- Uses `gemini-1.5-flash` (free tier: 15 requests/min)
- Good for testing or low-budget use

**Tips:**
- Increase `--interval` to reduce costs (30s = 1/3 the cost)
- Only run when you need monitoring
- Use Gemini free tier for testing

## Example Log Output

```
[2025-10-26 14:23:15] Empty room with hardwood floor. No movement detected.
[2025-10-26 14:23:25] Dog enters from left side, walking toward camera.
[2025-10-26 14:23:35] Dog sitting in center of room, looking at camera.
[2025-10-26 14:23:45] Dog lying down on floor, appears relaxed.
```

## Integration with Your App

You can integrate this into your backend by:

1. **Add to Celery worker** - Run as background task
2. **Store in database** - Save descriptions to PostgreSQL
3. **Real-time alerts** - Trigger notifications on specific activities
4. **Dashboard view** - Display activity timeline in frontend

Example integration:
```python
# backend/app/workers/activity_logger.py
from celery import shared_task
from stream_activity_logger import StreamActivityLogger

@shared_task
def log_stream_activity():
    logger = StreamActivityLogger(
        video_source=os.getenv("REMOTE_CAMERA_URL"),
        log_file="logs/stream_activity.txt",
        interval=30
    )
    logger.run()
```

## Troubleshooting

**"Failed to open video source"**
- Check camera URL is accessible
- Verify camera index (try 0, 1, 2)
- Ensure remote camera server is running

**"API key not set"**
- Set environment variable before running
- Check key is valid and has credits

**"Rate limit exceeded"**
- Increase `--interval` value
- Switch to Gemini free tier
- Check API usage dashboard

## Next Steps

- Add activity filtering (only log when movement detected)
- Store descriptions in database for better querying
- Add real-time alerts for specific activities
- Create web dashboard to view activity timeline
