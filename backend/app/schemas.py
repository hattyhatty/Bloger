from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


JsonDict = dict[str, Any]


class TopicIn(BaseModel):
    id: str
    source: str = "mock"
    title: str
    url: str = ""
    author: str = ""
    category: str = ""
    status: str = "DISCOVERED"
    score: int = 0
    raw: JsonDict = Field(default_factory=dict)


class TopicOut(TopicIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ContentIn(BaseModel):
    id: str
    topic_id: str | None = None
    title: str
    status: str = "DRAFT"
    platform: str = ""
    content_type: str = ""
    source_url: str = ""
    raw: JsonDict = Field(default_factory=dict)


class ContentOut(ContentIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeEntryIn(BaseModel):
    id: str
    topic_id: str | None = None
    content_id: str | None = None
    title: str
    body: str = ""
    source_url: str = ""
    tags: list[str] = Field(default_factory=list)
    raw: JsonDict = Field(default_factory=dict)


class KnowledgeEntryOut(KnowledgeEntryIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ActivityLogOut(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str
    details: JsonDict = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocalStorageCoreImportIn(BaseModel):
    topics: list[JsonDict] = Field(default_factory=list)
    contentItems: list[JsonDict] = Field(default_factory=list)
    knowledgeItems: list[JsonDict] = Field(default_factory=list)


class ImportBucketSummary(BaseModel):
    added: int = 0
    skipped: int = 0
    failed: int = 0


class ImportSummary(BaseModel):
    topics: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    contents: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    knowledge: ImportBucketSummary = Field(default_factory=ImportBucketSummary)


class MarkdownExportRequest(BaseModel):
    ids: list[str] = Field(default_factory=list)


class MarkdownFile(BaseModel):
    filename: str
    content: str


class MarkdownExportResponse(BaseModel):
    files: list[MarkdownFile]
