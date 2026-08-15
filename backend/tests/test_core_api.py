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


def test_business_workflow_crud_and_activity(client):
    client.post("/api/topics", json={"id": "topic_biz", "title": "Business Topic", "category": "AI Agent"})
    client.post("/api/contents", json={"id": "content_biz", "topic_id": "topic_biz", "title": "Business Content", "status": "APPROVED"})

    platform_version = {
        "id": "pv_content_biz_抖音_口播稿",
        "content_id": "content_biz",
        "platform": "抖音",
        "content_type": "口播稿",
        "title": "标题",
        "body": "脚本",
        "status": "Approved",
    }
    assert client.post("/api/platform-versions", json=platform_version).status_code == 200

    approval = {
        "id": "approval_content_biz",
        "content_id": "content_biz",
        "status": "Approved",
        "notes": "通过",
        "approved_at": "2026-08-15T19:00:00Z",
        "snapshot": {"title": "Business Content"},
    }
    assert client.post("/api/approvals", json=approval).json()["status"] == "Approved"

    publishing = {
        "id": "pub_biz",
        "content_id": "content_biz",
        "platform_version_id": "pv_content_biz_抖音_口播稿",
        "platform": "抖音",
        "content_type": "口播稿",
        "scheduled_at": "2026-08-16T19:00",
        "status": "Published",
        "url": "https://example.com/post",
    }
    assert client.post("/api/publishing-tasks", json=publishing).json()["status"] == "Published"

    analytics = {
        "id": "analytics_pub_biz",
        "publishing_task_id": "pub_biz",
        "content_id": "content_biz",
        "platform": "抖音",
        "content_type": "口播稿",
        "stats_date": "2026-08-17",
        "views": 1000,
        "likes": 120,
        "comments": 18,
        "shares": 25,
        "saves": 40,
        "followers_gained": 9,
        "tracking_status": "Tracking",
    }
    assert client.post("/api/analytics-records", json=analytics).json()["views"] == 1000

    snapshot = {
        "id": "track_analytics_pub_biz_24h",
        "publishing_task_id": "pub_biz",
        "analytics_record_id": "analytics_pub_biz",
        "checkpoint_id": "24h",
        "label": "发布后 24 小时",
        "status": "DONE",
        "metrics": {"views": 1000, "likes": 120},
    }
    assert client.post("/api/tracking-snapshots", json=snapshot).json()["status"] == "DONE"

    experience = {
        "id": "exp_pub_biz",
        "content_id": "content_biz",
        "topic_id": "topic_biz",
        "platform_version_id": "pv_content_biz_抖音_口播稿",
        "publishing_task_id": "pub_biz",
        "analytics_record_id": "analytics_pub_biz",
        "platform": "抖音",
        "content_type": "口播稿",
        "topic_category": "AI Agent",
        "performance_result": "high",
        "effective_practices": ["强 Hook"],
        "improvements": ["补充案例"],
    }
    assert client.post("/api/experience-records", json=experience).json()["performance_result"] == "high"

    assert client.get("/api/publishing-tasks").json()[0]["content_id"] == "content_biz"
    assert client.get("/api/tracking-snapshots").json()[0]["analytics_record_id"] == "analytics_pub_biz"
    assert client.get("/api/experience-records").json()[0]["topic_id"] == "topic_biz"

    activity = client.get("/api/activity-logs").json()
    entity_types = {item["entity_type"] for item in activity}
    assert {"ApprovalRecord", "PublishingTask", "TrackingSnapshot", "AnalyticsRecord", "ExperienceRecord"} <= entity_types


def test_business_localstorage_import_is_idempotent(client):
    client.post("/api/import/localstorage-core", json={
        "topics": [{"id": "topic_imp", "title": "Import Topic", "category": "AI Coding"}],
        "contentItems": [{"id": "content_imp", "title": "Import Content", "sourceTopicId": "topic_imp"}],
        "knowledgeItems": [],
    })
    payload = {
        "contentItems": [{
            "id": "content_imp",
            "title": "Import Content",
            "sourceTopicId": "topic_imp",
            "studioPlatform": "B站",
            "studioFormat": "长文",
            "draftTitle": "导入标题",
            "draftBody": "导入正文",
            "approvalStatus": "Approved",
            "approvedAt": "2026-08-15T12:00:00Z",
            "approvalSnapshot": {"title": "导入标题"},
        }],
        "generatedAssets": [],
        "publishJobs": [{
            "id": "job_imp",
            "contentId": "content_imp",
            "platform": "B站",
            "contentType": "长文",
            "scheduledAt": "2026-08-16T20:00",
            "status": "Published",
            "url": "https://example.com/bili",
        }],
        "analyticsRecords": [{
            "id": "analytics_imp",
            "publishJobId": "job_imp",
            "contentId": "content_imp",
            "platform": "B站",
            "contentType": "长文",
            "statsDate": "2026-08-17",
            "views": 300,
            "likes": 30,
            "trackingStatus": "Tracking",
            "checkpoints": [{
                "id": "24h",
                "label": "发布后 24 小时",
                "status": "DONE",
                "metrics": {"views": 300, "likes": 30},
            }],
        }],
        "experienceItems": [{
            "id": "exp_imp",
            "contentId": "content_imp",
            "topicId": "topic_imp",
            "publishJobId": "job_imp",
            "analyticsRecordId": "analytics_imp",
            "platform": "B站",
            "contentType": "长文",
            "topicCategory": "AI Coding",
            "performanceResult": "steady",
            "effectivePractices": ["教程结构清晰"],
            "improvements": ["标题更具体"],
        }],
    }

    first = client.post("/api/import/localstorage-business", json=payload).json()
    second = client.post("/api/import/localstorage-business", json=payload).json()

    assert first["platform_versions"]["added"] == 1
    assert first["approvals"]["added"] == 1
    assert first["publishing_tasks"]["added"] == 1
    assert first["analytics_records"]["added"] == 1
    assert first["tracking_snapshots"]["added"] == 1
    assert first["experience_records"]["added"] == 1
    assert second["platform_versions"]["skipped"] == 1
    assert second["approvals"]["skipped"] == 1
    assert second["publishing_tasks"]["skipped"] == 1
    assert second["analytics_records"]["skipped"] == 1
    assert second["tracking_snapshots"]["skipped"] == 1
    assert second["experience_records"]["skipped"] == 1
