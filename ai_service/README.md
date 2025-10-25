# AI Service - Dog Monitor

Mock AI service for dog monitoring application. Provides vision processing and coaching endpoints with simulated data.

## Features

- **Vision Processing**: Mock dog detection, pose estimation, action recognition, and object detection
- **AI Coach**: Training tips, session summaries, and chat interface

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
```

4. Run the service:
```bash
python main.py
```

The service will start on `http://localhost:8001`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Endpoints

### Vision Processing

**POST /vision/process**
- Processes video frames and returns mock detections
- Returns dog bounding boxes, pose keypoints, actions, and object detections

### Coach

**POST /coach/tips**
- Returns training tips based on current action

**POST /coach/summary**
- Generates session summary with wins, setbacks, and suggestions

**POST /coach/chat**
- Answers questions about training with timestamp references

## Mock Data

This service returns realistic mock data for development and testing:
- Dog detections with 75-95% confidence
- Pose keypoints (nose, shoulders, spine)
- Action classifications (sit, stand, lie, fetch-return, etc.)
- Object detections (ball, toy, bowl)
- Training tips and coaching advice

## Integration

The backend API service calls this AI service to process video frames. Configure the AI service URL in the backend's environment variables.
