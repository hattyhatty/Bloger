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


def test_knowledge_brain_retrieval_archive_and_creator_memory(client):
    client.post("/api/topics", json={"id": "topic_memory", "title": "Agent Memory", "category": "AI Agent"})
    client.post("/api/contents", json={"id": "content_memory", "topic_id": "topic_memory", "title": "Memory Content"})
    fact = {
        "id": "knowledge_fact",
        "topic_id": "topic_memory",
        "content_id": "content_memory",
        "title": "Agent memory needs evaluation",
        "body": "A verified research note about evaluation.",
        "knowledge_type": "Fact",
        "source": "Official research",
        "source_url": "https://example.com/research",
        "tags": ["Agent", "Memory"],
        "confidence": 94,
        "status": "ACTIVE",
    }
    inference = {
        **fact,
        "id": "knowledge_inference",
        "title": "Memory may improve retention",
        "body": "A hypothesis that still needs verification.",
        "knowledge_type": "Inference",
        "confidence": 58,
    }
    assert client.post("/api/knowledge", json=fact).status_code == 200
    assert client.post("/api/knowledge", json=inference).status_code == 200
    updated_inference = {**inference, "confidence": 61}
    assert client.put("/api/knowledge/knowledge_inference", json=updated_inference).json()["confidence"] == 61

    by_type = client.get("/api/knowledge", params={"type": "Fact", "tag": "Memory", "status": "ACTIVE"}).json()
    assert [item["id"] for item in by_type] == ["knowledge_fact"]
    related = client.get("/api/knowledge", params={"topic_id": "topic_memory", "q": "evaluation"}).json()
    assert [item["id"] for item in related] == ["knowledge_fact"]

    archived = client.post("/api/knowledge/knowledge_fact/archive").json()
    assert archived["status"] == "ARCHIVED"
    assert client.get("/api/knowledge", params={"status": "ACTIVE", "type": "Fact"}).json() == []

    creator_memory = {
        "account_positioning": "面向中文创作者的 AI 工作流账号",
        "target_audience": "独立创作者和 AI 产品从业者",
        "content_pillars": ["AI Agent", "AI Coding"],
        "tone_style": "清晰、克制、有实操细节",
        "preferred_formats": ["小红书图文", "B站长视频"],
        "topics_to_avoid": ["未经验证的模型传闻"],
        "platform_preferences": ["小红书", "B站"],
    }
    saved_memory = client.put("/api/creator-memory", json=creator_memory).json()
    assert saved_memory["id"] == "default"
    assert client.get("/api/creator-memory").json()["content_pillars"] == ["AI Agent", "AI Coding"]

    markdown = client.get("/api/knowledge/knowledge_inference/export.md").text
    assert "not a verified fact" in markdown
    activity_actions = {item["action"] for item in client.get("/api/activity-logs").json()}
    assert {"knowledge_created", "knowledge_updated", "knowledge_archived", "creator_memory_updated"} <= activity_actions


def test_knowledge_and_workspace_integrity(client):
    client.post("/api/topics", json={"id": "topic_other", "workspace_id": "other", "title": "Other Topic"})
    cross_workspace = client.post("/api/contents", json={
        "id": "content_cross",
        "workspace_id": "default",
        "topic_id": "topic_other",
        "title": "Cross workspace content",
    })
    assert cross_workspace.status_code == 409

    missing_source_fact = client.post("/api/knowledge", json={
        "id": "fact_without_source",
        "title": "Unverified claim",
        "knowledge_type": "Fact",
        "body": "This must not be stored as a verified fact.",
    })
    assert missing_source_fact.status_code == 409
    assert client.get("/api/knowledge", params={"workspace_id": "default"}).json() == []

    inference = client.post("/api/knowledge", json={
        "id": "inference_ok",
        "title": "A hypothesis",
        "knowledge_type": "Inference",
        "body": "Needs verification.",
        "confidence": 45,
    })
    assert inference.status_code == 200
    deleted = client.delete("/api/knowledge/inference_ok").json()
    assert deleted == {"ok": True, "archived": True}
    assert client.get("/api/knowledge", params={"status": "ARCHIVED"}).json()[0]["id"] == "inference_ok"


def test_unapproved_content_cannot_enter_publishing(client):
    client.post("/api/contents", json={"id": "content_unapproved", "title": "Unapproved"})
    client.post("/api/platform-versions", json={
        "id": "pv_unapproved",
        "content_id": "content_unapproved",
        "platform": "小红书",
        "content_type": "短帖",
        "title": "Title",
        "body": "Body",
    })
    response = client.post("/api/publishing-tasks", json={
        "id": "job_unapproved",
        "content_id": "content_unapproved",
        "platform_version_id": "pv_unapproved",
        "platform": "小红书",
        "content_type": "短帖",
        "scheduled_at": "2026-09-25T19:00",
        "status": "READY",
    })
    assert response.status_code == 409
    assert client.get("/api/publishing-tasks").json() == []


def test_localstorage_import_is_idempotent(client):
    payload = {
        "topics": [{"id": "topic_1", "title": "Topic", "category": "GPT"}],
        "contentItems": [{"id": "content_1", "title": "Content", "sourceTopicId": "topic_1"}],
        "knowledgeItems": [{"id": "knowledge_1", "title": "Knowledge", "summary": "Body", "linkedTopicId": "topic_1", "linkedContentIds": ["content_1"]}],
        "creatorMemory": {"accountPositioning": "AI 创作者", "contentPillars": ["AI Agent"]},
    }
    first = client.post("/api/import/localstorage-core", json=payload).json()
    second = client.post("/api/import/localstorage-core", json=payload).json()
    assert first["topics"]["added"] == 1
    assert second["topics"]["skipped"] == 1
    assert second["contents"]["skipped"] == 1
    assert second["knowledge"]["skipped"] == 1
    assert first["creator_memory"]["added"] == 1
    assert second["creator_memory"]["skipped"] == 1


def test_business_workflow_crud_and_activity(client):
    client.post("/api/topics", json={"id": "topic_biz", "title": "Business Topic", "category": "AI Agent"})
    content_payload = {
        "id": "content_biz",
        "topic_id": "topic_biz",
        "title": "Business Content",
        "status": "DRAFT",
        "platform": "抖音",
        "content_type": "口播稿",
        "source_url": "https://example.com/source",
        "raw": {"draftTitle": "标题", "draftBody": "脚本", "studioPlatform": "抖音", "studioFormat": "口播稿"},
    }
    created_content = client.post("/api/contents", json=content_payload).json()
    assert created_content["revision"] == 1
    assert created_content["content_hash"]

    platform_version = {
        "id": "pv_content_biz_douyin_r1",
        "content_id": "content_biz",
        "platform": "抖音",
        "content_type": "口播稿",
        "title": "标题",
        "hook": "Hook",
        "body": "脚本",
        "tags": ["AI"],
        "status": "DRAFT",
        "raw": {"sourceUrl": "https://example.com/source"},
    }
    saved_version = client.post("/api/platform-versions", json=platform_version).json()
    assert saved_version["revision"] == 1

    approval = {
        "id": "approval_content_biz",
        "content_id": "content_biz",
        "platform_version_id": "pv_content_biz_douyin_r1",
        "status": "APPROVED",
        "notes": "通过",
        "approved_at": "2026-08-15T19:00:00Z",
    }
    approved = client.post("/api/approvals", json=approval).json()
    assert approved["status"] == "APPROVED"
    assert approved["platform_version_id"] == saved_version["id"]
    assert approved["snapshot"]["contentHash"] == saved_version["content_hash"]

    duplicate_approval = client.post("/api/approvals", json={**approval, "id": "approval_retry"}).json()
    assert duplicate_approval["id"] == "approval_content_biz"

    immutable_change = client.put("/api/platform-versions/pv_content_biz_douyin_r1", json={**platform_version, "body": "静默改写"})
    assert immutable_change.status_code == 409
    client.post("/api/contents", json={"id": "content_other", "title": "Other Content"})
    rebound_version = client.put("/api/platform-versions/pv_content_biz_douyin_r1", json={**platform_version, "content_id": "content_other"})
    assert rebound_version.status_code == 409

    publishing = {
        "id": "pub_biz",
        "content_id": "content_biz",
        "platform_version_id": "pv_content_biz_douyin_r1",
        "platform": "抖音",
        "content_type": "口播稿",
        "scheduled_at": "2026-08-16T19:00",
        "status": "READY",
    }
    ready = client.post("/api/publishing-tasks", json=publishing).json()
    assert ready["status"] == "READY"
    assert ready["approval_record_id"] == approved["id"]
    assert ready["version_snapshot"]["contentHash"] == saved_version["content_hash"]
    duplicate_publish = client.post("/api/publishing-tasks", json={**publishing, "id": "pub_retry"}).json()
    assert duplicate_publish["id"] == "pub_biz"

    assert client.post("/api/publishing-tasks/pub_biz/tracking/start").status_code == 409
    assert client.put("/api/publishing-tasks/pub_biz", json={**publishing, "status": "PUBLISHED"}).status_code == 409
    published_payload = {
        **publishing,
        "status": "PUBLISHED",
        "actual_published_at": "2026-08-16T19:05:00Z",
        "url": "https://example.com/post",
    }
    published = client.put("/api/publishing-tasks/pub_biz", json=published_payload).json()
    assert published["status"] == "PUBLISHED"

    analytics = client.post("/api/publishing-tasks/pub_biz/tracking/start").json()
    assert analytics["tracking_status"] == "TRACKING"
    assert client.post("/api/publishing-tasks/pub_biz/tracking/start").json()["id"] == analytics["id"]

    snapshot = {
        "id": "track_analytics_pub_biz_24h_v1",
        "publishing_task_id": "pub_biz",
        "analytics_record_id": analytics["id"],
        "checkpoint_id": "24h",
        "label": "发布后 24 小时",
        "status": "DONE",
        "metrics": {"views": 1000, "likes": 120},
    }
    first_snapshot = client.post("/api/tracking-snapshots", json=snapshot).json()
    assert first_snapshot["sequence"] == 1
    second_snapshot = client.post("/api/tracking-snapshots", json={
        **snapshot,
        "id": "track_analytics_pub_biz_24h_v2",
        "metrics": {"views": 1400, "likes": 180},
    }).json()
    assert second_snapshot["sequence"] == 2
    assert client.put("/api/tracking-snapshots/track_analytics_pub_biz_24h_v1", json={**snapshot, "metrics": {"views": 9999}}).status_code == 409
    analytics_latest = client.get("/api/analytics-records").json()[0]
    assert analytics_latest["views"] == 1400
    assert len(client.get("/api/tracking-snapshots").json()) == 2

    experience = {
        "id": "exp_pub_biz",
        "content_id": "content_biz",
        "topic_id": "topic_biz",
        "platform_version_id": "pv_content_biz_douyin_r1",
        "publishing_task_id": "pub_biz",
        "analytics_record_id": analytics["id"],
        "platform": "抖音",
        "content_type": "口播稿",
        "topic_category": "AI Agent",
        "performance_result": "high",
        "effective_practices": ["强 Hook"],
        "improvements": ["补充案例"],
    }
    assert client.post("/api/experience-records", json=experience).json()["performance_result"] == "high"
    assert client.post("/api/experience-records", json={**experience, "id": "exp_retry"}).json()["id"] == "exp_pub_biz"

    assert client.get("/api/publishing-tasks").json()[0]["content_id"] == "content_biz"
    assert client.get("/api/tracking-snapshots").json()[0]["analytics_record_id"] == analytics["id"]
    assert client.get("/api/experience-records").json()[0]["topic_id"] == "topic_biz"

    changed_content = client.put("/api/contents/content_biz", json={
        **content_payload,
        "raw": {**content_payload["raw"], "draftBody": "批准后修改的新脚本"},
    }).json()
    assert changed_content["revision"] == 2
    assert client.get("/api/approvals").json()[0]["status"] == "DRAFT"
    historical_job = client.get("/api/publishing-tasks").json()[0]
    assert historical_job["version_snapshot"]["body"] == "脚本"
    historical_revision = historical_job["content_revision"]
    resaved_published_job = client.put("/api/publishing-tasks/pub_biz", json={**published_payload, "notes": "补充发布备注"}).json()
    assert resaved_published_job["content_revision"] == historical_revision
    assert resaved_published_job["version_snapshot"]["body"] == "脚本"
    assert resaved_published_job["approval_record_id"] == approved["id"]

    activity = client.get("/api/activity-logs").json()
    activity_actions = {item["action"] for item in activity}
    assert {"content_approved", "publishing_task_created", "content_published", "tracking_started", "tracking_snapshot_created", "analytics_updated", "performance_review_generated", "approval_invalidated"} <= activity_actions


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
