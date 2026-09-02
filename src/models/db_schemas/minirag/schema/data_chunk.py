from .minirag_base import Base
from sqlalchemy import Integer, Column, Text, ForeignKey, Index, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import uuid

class DataChunk(Base):
    __tablename__ = "data_chunks"

    chunk_id = Column(Integer, primary_key=True)
    chunk_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    chunk_text = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_order = Column(Integer, nullable=True)

    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    project = relationship("Project", back_populates="chunks")
    asset = relationship("Asset", back_populates="chunks")

    __tableargs__ = (
        Index('ix_project_id', chunk_project_id)
    )

class RetrievedDocument(BaseModel):
    text: str
    score: float