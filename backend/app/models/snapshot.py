from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ts = Column(TIMESTAMP, nullable=False)
    s3_uri = Column(String(500), nullable=False)
    labels = Column(ARRAY(String), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="snapshots")

    __table_args__ = (
        Index("idx_snapshots_user_ts", "user_id", "ts"),
    )
