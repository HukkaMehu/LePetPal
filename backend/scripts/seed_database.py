"""
Database seeding script for demo mode.
Creates sample users, events, metrics, clips, and snapshots.
"""
import sys
import os
from datetime import datetime, timedelta
import random
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import User, Event, Clip, Snapshot, AIMetricsDaily, Routine, Device, Model


def create_demo_user(db: Session) -> User:
    """Create or get demo user."""
    demo_email = "demo@dogmonitor.com"
    user = db.query(User).filter(User.email == demo_email).first()
    
    if not user:
        user = User(
            id=uuid.uuid4(),
            email=demo_email,
            role="owner"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created demo user: {user.email}")
    else:
        print(f"✓ Demo user already exists: {user.email}")
    
    return user


def create_sample_events(db: Session, user: User, days: int = 7):
    """Create sample events for the past N days."""
    event_types = [
        ("sit", {"confidence": 0.95, "duration_sec": 5}),
        ("stand", {"confidence": 0.92, "duration_sec": 3}),
        ("lie", {"confidence": 0.88, "duration_sec": 120}),
        ("fetch_return", {"confidence": 0.85, "success": True}),
        ("fetch_return", {"confidence": 0.80, "success": False}),
        ("bark", {"volume": 0.7, "duration_sec": 2}),
        ("howl", {"volume": 0.6, "duration_sec": 4}),
        ("whine", {"volume": 0.4, "duration_sec": 1}),
        ("dog_detected", {"confidence": 0.98, "box": {"x": 100, "y": 150, "w": 200, "h": 250}}),
        ("person_entered", {"confidence": 0.90}),
        ("drinking", {"confidence": 0.85, "duration_sec": 10}),
        ("eating", {"confidence": 0.88, "duration_sec": 30}),
        ("bookmark", {"label": "Good sit!", "manual": True}),
        ("clip_saved", {"duration_ms": 10000, "labels": ["fetch", "success"]}),
    ]
    
    events_created = 0
    now = datetime.now()
    
    for day_offset in range(days):
        day_start = now - timedelta(days=day_offset)
        
        # Generate 20-50 events per day
        num_events = random.randint(20, 50)
        
        for _ in range(num_events):
            # Random time during the day
            hour = random.randint(6, 22)  # Active hours 6am-10pm
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            event_ts = day_start.replace(hour=hour, minute=minute, second=second)
            event_type, event_data = random.choice(event_types)
            
            # Video timestamp in milliseconds (simulated)
            video_ts_ms = (hour * 3600 + minute * 60 + second) * 1000
            
            event = Event(
                id=uuid.uuid4(),
                user_id=user.id,
                ts=event_ts,
                type=event_type,
                data=event_data,
                video_ts_ms=video_ts_ms
            )
            db.add(event)
            events_created += 1
    
    db.commit()
    print(f"✓ Created {events_created} sample events over {days} days")


def create_sample_metrics(db: Session, user: User, days: int = 7):
    """Create sample daily metrics."""
    now = datetime.now()
    
    for day_offset in range(days):
        date = (now - timedelta(days=day_offset)).date()
        
        # Check if metrics already exist
        existing = db.query(AIMetricsDaily).filter(
            AIMetricsDaily.user_id == user.id,
            AIMetricsDaily.date == date
        ).first()
        
        if existing:
            continue
        
        # Generate realistic metrics with some variation
        base_sit = 15
        base_stand = 25
        base_lie = 10
        
        metrics = AIMetricsDaily(
            id=uuid.uuid4(),
            user_id=user.id,
            date=date,
            sit_count=base_sit + random.randint(-5, 10),
            stand_count=base_stand + random.randint(-8, 12),
            lie_count=base_lie + random.randint(-3, 8),
            fetch_count=random.randint(5, 15),
            fetch_success_count=random.randint(3, 12),
            treats_dispensed=random.randint(8, 20),
            time_in_frame_min=random.randint(180, 420),  # 3-7 hours
            barks=random.randint(5, 25),
            howls=random.randint(0, 5),
            whines=random.randint(0, 8),
            calm_minutes=random.randint(60, 180)  # 1-3 hours
        )
        db.add(metrics)
    
    db.commit()
    print(f"✓ Created sample metrics for {days} days")


def create_sample_clips(db: Session, user: User, count: int = 10):
    """Create sample clip records."""
    labels_options = [
        ["fetch", "success"],
        ["sit", "training"],
        ["play", "toy"],
        ["treat", "reward"],
        ["bark", "alert"],
        ["zoomies", "energy"],
    ]
    
    now = datetime.now()
    
    for i in range(count):
        # Random timestamp in the past week
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        
        start_ts = now - timedelta(days=days_ago, hours=hours_ago)
        duration_ms = random.randint(8000, 15000)  # 8-15 seconds
        
        clip = Clip(
            id=uuid.uuid4(),
            user_id=user.id,
            start_ts=start_ts,
            duration_ms=duration_ms,
            s3_uri=f"s3://dog-monitor/clips/demo_{uuid.uuid4()}.mp4",
            labels=random.choice(labels_options),
            preview_png=f"s3://dog-monitor/clips/demo_{uuid.uuid4()}_preview.png",
            share_token=str(uuid.uuid4())[:8]
        )
        db.add(clip)
    
    db.commit()
    print(f"✓ Created {count} sample clips")


def create_sample_snapshots(db: Session, user: User, count: int = 15):
    """Create sample snapshot records."""
    labels_options = [
        ["sleeping", "cute"],
        ["playing", "toy"],
        ["sitting", "good-boy"],
        ["alert", "watching"],
        ["eating", "meal-time"],
        ["portrait", "adorable"],
    ]
    
    notes = [
        "Such a good boy!",
        "Perfect sit position",
        "Caught mid-yawn",
        "Waiting patiently",
        "Play time!",
        None,
        None,
    ]
    
    now = datetime.now()
    
    for i in range(count):
        # Random timestamp in the past week
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        
        ts = now - timedelta(days=days_ago, hours=hours_ago)
        
        snapshot = Snapshot(
            id=uuid.uuid4(),
            user_id=user.id,
            ts=ts,
            s3_uri=f"s3://dog-monitor/snapshots/demo_{uuid.uuid4()}.jpg",
            labels=random.choice(labels_options),
            note=random.choice(notes)
        )
        db.add(snapshot)
    
    db.commit()
    print(f"✓ Created {count} sample snapshots")


def create_sample_routines(db: Session, user: User):
    """Create sample training routines."""
    routines_data = [
        {
            "name": "Morning Training",
            "cron": "0 8 * * *",  # 8 AM daily
            "steps": [
                {"type": "sit_drill", "duration": 300},
                {"type": "treat", "params": {"count": 1}},
                {"type": "fetch", "duration": 600},
                {"type": "treat", "params": {"count": 1}},
            ],
            "enabled": True
        },
        {
            "name": "Afternoon Play",
            "cron": "0 15 * * *",  # 3 PM daily
            "steps": [
                {"type": "play", "duration": 900},
                {"type": "fetch", "duration": 600},
                {"type": "wait", "duration": 120},
                {"type": "treat", "params": {"count": 2}},
            ],
            "enabled": True
        },
        {
            "name": "Evening Calm",
            "cron": "0 20 * * *",  # 8 PM daily
            "steps": [
                {"type": "pet", "duration": 180},
                {"type": "sit_drill", "duration": 180},
                {"type": "treat", "params": {"count": 1}},
            ],
            "enabled": False
        },
    ]
    
    for routine_data in routines_data:
        routine = Routine(
            id=uuid.uuid4(),
            user_id=user.id,
            name=routine_data["name"],
            cron=routine_data["cron"],
            steps=routine_data["steps"],
            enabled=routine_data["enabled"]
        )
        db.add(routine)
    
    db.commit()
    print(f"✓ Created {len(routines_data)} sample routines")


def create_sample_models(db: Session):
    """Create sample AI model records."""
    models_data = [
        {
            "name": "yolov8n-dog",
            "type": "detector",
            "artifact_uri": "s3://dog-monitor/models/yolov8n-dog.pt",
            "version": "1.0.0",
            "status": "active",
            "metadata": {"accuracy": 0.92, "fps": 30}
        },
        {
            "name": "yolov8s-dog",
            "type": "detector",
            "artifact_uri": "s3://dog-monitor/models/yolov8s-dog.pt",
            "version": "1.0.0",
            "status": "available",
            "metadata": {"accuracy": 0.95, "fps": 20}
        },
        {
            "name": "action-recognizer-v1",
            "type": "action",
            "artifact_uri": "s3://dog-monitor/models/action-v1.onnx",
            "version": "1.0.0",
            "status": "active",
            "metadata": {"classes": ["sit", "stand", "lie", "fetch"]}
        },
        {
            "name": "pose-estimator-lite",
            "type": "pose",
            "artifact_uri": "s3://dog-monitor/models/pose-lite.pt",
            "version": "1.0.0",
            "status": "active",
            "metadata": {"keypoints": 17}
        },
    ]
    
    for model_data in models_data:
        # Check if model already exists
        existing = db.query(Model).filter(
            Model.name == model_data["name"],
            Model.version == model_data["version"]
        ).first()
        
        if existing:
            continue
        
        model = Model(
            id=uuid.uuid4(),
            name=model_data["name"],
            type=model_data["type"],
            artifact_uri=model_data["artifact_uri"],
            version=model_data["version"],
            status=model_data["status"],
            model_metadata=model_data["metadata"]
        )
        db.add(model)
    
    db.commit()
    print(f"✓ Created sample AI models")


def seed_database():
    """Main seeding function."""
    print("\n🌱 Starting database seeding...\n")
    
    db = SessionLocal()
    
    try:
        # Create demo user
        user = create_demo_user(db)
        
        # Create sample data
        create_sample_events(db, user, days=7)
        create_sample_metrics(db, user, days=7)
        create_sample_clips(db, user, count=10)
        create_sample_snapshots(db, user, count=15)
        create_sample_routines(db, user)
        create_sample_models(db)
        
        print("\n✅ Database seeding completed successfully!\n")
        print(f"Demo user email: demo@dogmonitor.com")
        print(f"Demo user ID: {user.id}\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}\n")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
