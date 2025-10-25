# Starting the Celery Worker

## The Problem

Your clips are stuck in "processing" status because **the Celery worker is not running**.

When you create a clip:
1. ✅ Backend API creates a database record
2. ✅ Backend queues a background job
3. ❌ **Celery worker should process the job** ← THIS IS NOT RUNNING
4. ❌ Video file never gets created

## Solution: Start Celery Worker

You need to run the Celery worker in a **separate terminal** alongside your backend.

### Windows

Open a new terminal and run:

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

### macOS/Linux

```bash
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

## What You Should See

When Celery starts successfully, you'll see:

```
 -------------- celery@YOUR-COMPUTER v5.x.x
---- **** -----
--- * ***  * -- Windows-10.x.x
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         app.core.celery_app
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . process_clip

[2025-10-25 19:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-25 19:00:00,000: INFO/MainProcess] celery@YOUR-COMPUTER ready.
```

## Testing

After starting Celery:

1. **Record a new clip** through the UI
2. **Watch the Celery terminal** - you should see:
   ```
   [2025-10-25 19:00:05,000: INFO/MainProcess] Task process_clip[xxx] received
   [2025-10-25 19:00:06,000: INFO/MainProcess] Processing clip xxx
   [2025-10-25 19:00:08,000: INFO/MainProcess] Clip xxx processed successfully
   [2025-10-25 19:00:08,000: INFO/MainProcess] Task process_clip[xxx] succeeded
   ```
3. **Check the gallery** - clip should now be playable!

## Process Existing Stuck Clips

If you have clips stuck in "processing" status, you can:

### Option 1: Delete and Re-record
1. Delete the stuck clips through the UI
2. Record new ones (with Celery running)

### Option 2: Manually Trigger Processing
```bash
cd backend
python scripts/reprocess_stuck_clips.py
```

(I'll create this script for you)

## Running Everything Together

You need **3 terminals** for full functionality:

### Terminal 1: Backend API
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Celery Worker
```bash
cd backend
venv\Scripts\activate
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Frontend
```bash
cd "Pet Training Web App"
npm run dev
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'celery'"
**Solution**: Install Celery
```bash
cd backend
venv\Scripts\activate
pip install celery redis
```

### "Cannot connect to redis"
**Solution**: Start Redis with Docker
```bash
docker-compose up -d redis
```

### Celery starts but tasks don't process
**Solution**: Check Redis connection in `.env`:
```
REDIS_URL=redis://localhost:6379/0
```

## Why This Wasn't Documented

The Celery worker requirement was missing from all the startup documentation. This is a common oversight in development setups. The worker is essential for:

- Processing video clips
- Handling background event processing
- Any async/scheduled tasks

Without it, tasks get queued but never executed!
