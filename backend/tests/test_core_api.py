import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_topic_content_knowledge_crud_and_activity(client):
    topic = {"id": "topic_1", "source": "mock", "title": "Agent news", "category": "AI Agent", "raw": {"tags": ["AI Agent"]}}
    assert client.post("/api/topics", json=topic).status_code == 200
    assert client.get("/api/topics").json()[0]["id"] == "topic_1"

    content = {"id": "content_1", "topic_id": "topic_1", "title": "Agent 内容", "status": "DRAFT", "raw": {"sourceTopicId": "topic_1"}}
    assert client.post("/api/contents", json=content).status_code == 200
    updated = {**content, "status": "APPROVED"}
    assert client.put("/api/contents/content_1", json=updated).json()["status"] == "APPROVED"

    knowledge = {"id": "knowledge_1", "topic_id": "topic_1", "content_id": "content_1", "title": "经验", "body": "正文", "tags": ["AI"], "source_url": "https://example.com"}
    assert client.post("/api/knowledge", json=knowledge).status_code == 200
    markdown = client.get("/api/knowledge/knowledge_1/export.md").text
    assert "topic_id" in markdown
    assert "# 经验" in markdown

    activity = client.get("/api/activity-logs").json()
    assert any(item["entity_type"] == "KnowledgeEntry" for item in activity)


def test_localstorage_import_is_idempotent(client):
    payload = {
        "topics": [{"id": "topic_1", "title": "Topic", "category": "GPT"}],
        "contentItems": [{"id": "content_1", "title": "Content", "sourceTopicId": "topic_1"}],
        "knowledgeItems": [{"id": "knowledge_1", "title": "Knowledge", "summary": "Body", "linkedTopicId": "topic_1", "linkedContentIds": ["content_1"]}],
    }
    first = client.post("/api/import/localstorage-core", json=payload).json()
    second = client.post("/api/import/localstorage-core", json=payload).json()
    assert first["topics"]["added"] == 1
    assert second["topics"]["skipped"] == 1
    assert second["contents"]["skipped"] == 1
    assert second["knowledge"]["skipped"] == 1
