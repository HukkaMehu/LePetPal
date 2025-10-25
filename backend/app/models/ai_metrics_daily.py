from sqlalchemy import Column, Date, Integer, TIMESTAMP, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class AIMetricsDaily(Base):
    __tablename__ = "ai_metrics_daily"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    sit_count = Column(Integer, default=0)
    stand_count = Column(Integer, default=0)
    lie_count = Column(Integer, default=0)
    fetch_count = Column(Integer, default=0)
    fetch_success_count = Column(Integer, default=0)
    treats_dispensed = Column(Integer, default=0)
    time_in_frame_min = Column(Integer, default=0)
    barks = Column(Integer, default=0)
    howls = Column(Integer, default=0)
    whines = Column(Integer, default=0)
    calm_minutes = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ai_metrics")

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date"),
        Index("idx_metrics_user_date", "user_id", "date"),
    )
