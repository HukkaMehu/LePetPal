from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create Base first so models can import it
Base = declarative_base()

# Import all models here so Alembic can detect them
from app.models import (  # noqa: E402, F401
    User,
    Device,
    Event,
    Clip,
    Snapshot,
    Routine,
    AIMetricsDaily,
    Model,
)

# Create engine and session after models are imported
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
