import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from .session import Base

def now() -> datetime:
    return datetime.utcnow()

class Collection(Base):
    __tablename__ = "collections"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(200))
    latest_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_collection_slug"),)

class RagChunk(Base):
    __tablename__ = "rag_chunks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    doc_id: Mapped[str] = mapped_column(String(200))
    embedding: Mapped[list] = mapped_column(Vector(1536))
    content: Mapped[str] = mapped_column(Text)
    # Attribute 'meta' mapped to DB column 'metadata'
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    __table_args__ = (UniqueConstraint("collection_id", "version", "doc_id", name="uq_chunk_key"),)
