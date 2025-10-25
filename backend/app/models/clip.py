from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer, Index, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Clip(Base):
    __tablename__ = "clips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_ts = Column(TIMESTAMP, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    s3_uri = Column(String(500), nullable=False)
    labels = Column(ARRAY(String), nullable=True)
    preview_png = Column(String(500), nullable=True)
    share_token = Column(String(100), unique=True, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="clips")

    __table_args__ = (
        Index("idx_clips_user_start", "user_id", "start_ts"),
    )
