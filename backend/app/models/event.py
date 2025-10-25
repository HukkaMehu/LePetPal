from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, BigInteger, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ts = Column(TIMESTAMP, nullable=False, index=True)
    type = Column(String(100), nullable=False)
    data = Column(JSONB, nullable=True)
    video_ts_ms = Column(BigInteger, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="events")

    __table_args__ = (
        Index("idx_events_user_type_ts", "user_id", "type", "ts"),
        Index("idx_events_video_ts", "video_ts_ms", postgresql_where=(video_ts_ms.isnot(None))),
    )
