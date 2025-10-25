# 🚨 CELERY WORKER REQUIRED FOR VIDEO CLIPS

## The Issue

Your clips are **stuck in "processing" status** because the **Celery worker is not running**.

## Quick Fix

Open a **new terminal** and run:

```bash
cd backend
venv\Scripts\activate
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

Or use the batch file:
```bash
cd backend
start_celery_worker.bat
```

## What This Does

The Celery worker processes background jobs, including:
- Creating video files from clip requests
- Processing events
- Any async tasks

Without it, clips get created in the database but never processed into actual video files.

## Full Startup Process

You need **3 terminals** running simultaneously:

### Terminal 1: Backend API ✅ (You have this)
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Celery Worker ❌ (You're missing this!)
```bash
cd backend
venv\Scripts\activate
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Frontend ✅ (You have this)
```bash
cd "Pet Training Web App"
npm run dev
```

## After Starting Celery

### For New Clips
1. Record a new clip through the UI
2. Watch the Celery terminal for processing logs
3. Clip should appear in gallery and be playable

### For Existing Stuck Clips

**Option 1: Delete and re-record** (Easiest)
- Delete stuck clips through the UI
- Record new ones

**Option 2: Reprocess stuck clips**
```bash
cd backend
python scripts/reprocess_stuck_clips.py
```

This will requeue all stuck clips for processing.

## Verification

After starting Celery and recording a clip, you should see in the Celery terminal:

```
[INFO] Task process_clip[xxx] received
[INFO] Processing clip xxx
[INFO] Uploaded file to s3://dog-monitor/clips/...
[INFO] Clip xxx processed successfully
[INFO] Task process_clip[xxx] succeeded in 2.5s
```

And in the gallery, the clip should:
- ✅ Have a preview thumbnail
- ✅ Play when clicked
- ✅ Download as .mp4
- ✅ Show correct duration

## Why This Happened

The Celery worker requirement was missing from all documentation. This is a common oversight - the backend API can run without Celery, but background tasks won't process.

## Dependencies

If you get "ModuleNotFoundError: No module named 'celery'":

```bash
cd backend
venv\Scripts\activate
pip install celery redis
```

Make sure Redis is running:
```bash
docker-compose up -d redis
```

## Summary

**Before**: Backend API running → Clips created but stuck in "processing"

**After**: Backend API + Celery worker running → Clips processed into playable videos

Start Celery now and your videos will work! 🎉
