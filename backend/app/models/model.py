from sqlalchemy import Column, String, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db.base import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'detector', 'action', 'pose', 'policy'
    artifact_uri = Column(String(500), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="available")
    model_metadata = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_model_name_version"),
    )
