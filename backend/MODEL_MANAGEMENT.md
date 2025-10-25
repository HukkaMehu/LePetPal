# AI Model Management Implementation

This document describes the AI model management feature that allows runtime model switching.

## Overview

The model management system enables hot-swapping of AI models without restarting services. This includes:
- Dog detection models
- Action recognition models  
- Pose estimation models
- Policy models (for robot control)

**Requirements Addressed:** 12.1, 12.2, 12.3, 12.4, 12.5

## Architecture

### Backend API (`backend/app/api/models.py`)

**Endpoints:**

1. `GET /api/models`
   - Lists all available models from database
   - Returns currently active model for each type
   - Response includes model metadata and status

2. `POST /api/models/switch`
   - Accepts model names to switch (detector, action_recognizer, pose_estimator, policy)
   - Validates models exist in database
   - Calls AI service to perform hot-swap
   - Updates database with new active models
   - Returns success status and any errors

### AI Service (`ai_service/api/models.py`)

**Endpoints:**

1. `POST /models/switch`
   - Validates requested models for compatibility
   - Loads new models in parallel
   - Atomically switches active models
   - Unloads old models in background
   - Maintains detection continuity with <2s interruption

2. `GET /models/active`
   - Returns currently active model for each type

3. `GET /models/status`
   - Returns detailed status of all loaded models
   - Includes load time and status

**Model Manager:**

The `ModelManager` class handles:
- Model validation (format, compatibility, dependencies)
- Model loading (download, initialize, warm-up)
- Model unloading (release GPU memory, cleanup)
- Hot-swap orchestration with minimal interruption
- Thread-safe switching with async lock

### Frontend UI

**Settings Page (`frontend/src/app/settings/page.tsx`):**
- Main settings page at `/settings` route
- Contains model management section
- Placeholder sections for future settings

**Model Selector Component (`frontend/src/components/ModelSelector.tsx`):**
- Displays current active models
- Dropdown selectors for each model type
- Apply changes button
- Real-time status messages (success/error)
- Refresh button to reload model list

## Usage

### Starting Services

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# AI Service  
cd ai_service
python main.py

# Frontend
cd frontend
npm run dev
```

### Using the UI

1. Navigate to http://localhost:3000/settings
2. View currently active models in the blue info box
3. Select new models from dropdowns
4. Click "Apply Changes" to switch models
5. Wait for confirmation message (typically 1-2 seconds)

### API Examples

**List Models:**
```bash
curl http://localhost:8000/api/models
```

**Switch Models:**
```bash
curl -X POST http://localhost:8000/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{
    "detector": "yolo-v8-small@1.1",
    "action_recognizer": "action-transformer-base@2.0"
  }'
```

**Check AI Service Status:**
```bash
curl http://localhost:8001/models/status
```

## Database Schema

Models are stored in the `models` table:

```sql
CREATE TABLE models (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,  -- 'detector', 'action', 'pose', 'policy'
  artifact_uri VARCHAR(500) NOT NULL,
  version VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'available',  -- 'available', 'active', 'error'
  model_metadata JSONB,
  created_at TIMESTAMP NOT NULL,
  UNIQUE(name, version)
);
```

## Hot-Swap Process

The model switching process follows these phases:

1. **Validation Phase**
   - Check all requested models exist in database
   - Verify models are not in error state
   - Validate model compatibility

2. **Loading Phase**
   - Load new models in parallel (reduces switch time)
   - Download artifacts if needed
   - Initialize models for inference
   - Warm up with dummy input

3. **Switch Phase**
   - Atomically update active model references
   - Update database status
   - Minimal interruption (<2s)

4. **Cleanup Phase**
   - Unload old models in background
   - Release GPU memory
   - Clean up resources

## Error Handling

**Backend Errors:**
- Model not found → 400 Bad Request with details
- AI service timeout → Returns error with timeout message
- AI service unavailable → Returns connection error
- Database error → Rolls back transaction

**AI Service Errors:**
- Validation failure → Returns specific validation errors
- Loading failure → Returns loading error details
- Switch failure → Maintains previous active models

**Frontend Errors:**
- API errors displayed in red alert box
- Success messages displayed in green alert box
- Loading states shown with spinners
- Retry functionality available

## Testing

To test the implementation:

1. **Seed Database with Models:**
   ```sql
   INSERT INTO models (name, type, artifact_uri, version, status) VALUES
   ('yolo-v8-nano', 'detector', 's3://models/yolo-v8-nano.pt', '1.0', 'active'),
   ('yolo-v8-small', 'detector', 's3://models/yolo-v8-small.pt', '1.1', 'available'),
   ('action-transformer-lite', 'action', 's3://models/action-lite.pt', '1.0', 'active'),
   ('pose-lite', 'pose', 's3://models/pose-lite.pt', '1.0', 'active');
   ```

2. **Test API Endpoints:**
   - Use curl or Postman to test endpoints
   - Verify responses match expected format
   - Test error cases (invalid models, service down)

3. **Test UI:**
   - Navigate to settings page
   - Verify dropdowns populate with models
   - Test switching models
   - Verify success/error messages
   - Test refresh functionality

## Future Enhancements

- Model performance metrics tracking
- Automatic model selection based on hardware
- Model A/B testing framework
- Model version rollback capability
- Model download progress indicators
- Model compatibility matrix display

## Requirements Mapping

- **12.1**: GET /api/models lists available models ✓
- **12.2**: POST /api/models/switch performs hot-swap ✓
- **12.3**: Model validation before switching ✓
- **12.4**: Detection continuity maintained (<2s interruption) ✓
- **12.5**: Settings UI displays and switches models ✓
