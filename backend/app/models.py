from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

JsonType = JSON().with_variant(JSONB, "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Topic(Base, TimestampMixin):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    source: Mapped[str] = mapped_column(String(64), index=True, default="mock")
    title: Mapped[str] = mapped_column(String(512), index=True)
    url: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(255), default="")
    category: Mapped[str] = mapped_column(String(128), index=True, default="")
    status: Mapped[str] = mapped_column(String(64), index=True, default="DISCOVERED")
    score: Mapped[int] = mapped_column(Integer, default=0)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    contents: Mapped[list["Content"]] = relationship(back_populates="topic")
    knowledge_entries: Mapped[list["KnowledgeEntry"]] = relationship(back_populates="topic")


class Content(Base, TimestampMixin):
    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    topic_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("topics.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True, default="DRAFT")
    platform: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_type: Mapped[str] = mapped_column(String(64), index=True, default="")
    source_url: Mapped[str] = mapped_column(Text, default="")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    topic: Mapped[Topic | None] = relationship(back_populates="contents")
    knowledge_entries: Mapped[list["KnowledgeEntry"]] = relationship(back_populates="content")


class KnowledgeEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_entries"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    topic_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("topics.id"), nullable=True, index=True)
    content_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("contents.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    body: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list] = mapped_column(JsonType, default=list)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    topic: Mapped[Topic | None] = relationship(back_populates="knowledge_entries")
    content: Mapped[Content | None] = relationship(back_populates="knowledge_entries")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    details: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)
