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
    assert client.put("/api/contents/content_1", json=updated).json()["status"] == "DRAFT"

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
    unapproved = client.post("/api/contents", json={"id": "content_unapproved", "title": "Unapproved", "status": "PUBLISHED"}).json()
    assert unapproved["status"] == "DRAFT"
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
        "opportunityItems": [{
            "id": "opportunity_import_1",
            "topicId": "topic_1",
            "creatorProfileId": "default",
            "analysisBatchId": "batch_import_1",
            "knowledgeIds": ["knowledge_1"],
            "contentOpportunity": "把 GPT 热点解释成创作者行动清单",
            "recommendedFormat": "短帖",
            "platformFit": ["小红书"],
            "novelty": 75,
            "timeliness": 80,
            "audienceFit": 85,
            "creatorFit": 90,
            "humanNeedStrength": 70,
            "platformFitScore": 85,
            "visualPotential": 60,
            "productionDifficulty": 35,
            "reasoning": "匹配创作者定位。",
        }],
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
    assert first["opportunities"]["added"] == 1
    assert second["opportunities"]["skipped"] == 1


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


def opportunity_candidate(candidate_id: str, angle: str, score_shift: int = 0):
    return {
        "id": candidate_id,
        "summary": "AI Agent 产品发布带来新的创作切口。",
        "why_it_matters": "它把复杂技术转化为普通创作者可使用的工作流。",
        "audience": "希望提升效率的中文独立创作者",
        "underlying_need_or_emotion": "害怕落后，同时希望获得可执行的方法",
        "content_opportunity": angle,
        "recommended_format": "口播稿",
        "platform_fit": ["抖音", "B站"],
        "novelty": 80 + score_shift,
        "timeliness": 90,
        "audience_fit": 75,
        "creator_fit": 85,
        "human_need_strength": 70,
        "platform_fit_score": 80,
        "visual_potential": 60,
        "production_difficulty": 40,
        "overall_score": 1,
        "reasoning": "题目新鲜、与账号定位一致，并能给目标受众明确行动建议。",
    }


def test_research_opportunity_develop_workflow(client):
    assert client.post("/api/topics", json={
        "id": "topic_opportunity",
        "title": "OpenAI releases an agent workflow",
        "category": "AI Agent",
        "url": "https://example.com/agent",
        "raw": {"tags": ["Agent", "Creator"], "publishedAt": "2026-09-25"},
    }).status_code == 200
    assert client.put("/api/creator-memory", json={
        "account_positioning": "帮助中文独立创作者掌握 AI 工作流",
        "target_audience": "中文独立创作者",
        "content_pillars": ["AI Agent", "Creator Productivity"],
        "preferred_formats": ["口播稿"],
        "topics_to_avoid": ["未经证实的传闻"],
        "platform_preferences": ["抖音", "B站"],
    }).status_code == 200
    fact = {
        "id": "knowledge_opportunity_fact",
        "topic_id": "topic_opportunity",
        "title": "Official agent release note",
        "body": "The official release documents an agent workflow.",
        "knowledge_type": "Fact",
        "source": "Official release",
        "source_url": "https://example.com/agent",
        "tags": ["Agent"],
        "confidence": 95,
        "status": "ACTIVE",
    }
    inference = {
        **fact,
        "id": "knowledge_opportunity_inference",
        "title": "Creators may adopt agents faster",
        "body": "This remains a hypothesis.",
        "knowledge_type": "Inference",
        "source": "Internal analysis",
        "source_url": "",
        "confidence": 55,
    }
    assert client.post("/api/knowledge", json=fact).status_code == 200
    assert client.post("/api/knowledge", json=inference).status_code == 200

    context = client.get("/api/topics/topic_opportunity/opportunity-context").json()
    assert context["creator_memory"]["target_audience"] == "中文独立创作者"
    assert {item["knowledge_type"] for item in context["knowledge"]} == {"Fact", "Inference"}

    analysis = {
        "topic_id": "topic_opportunity",
        "creator_profile_id": context["creator_memory"]["id"],
        "analysis_batch_id": "batch_opportunity_1",
        "knowledge_ids": [item["id"] for item in context["knowledge"]],
        "opportunities": [
            opportunity_candidate("opportunity_1", "普通创作者如何用 Agent 节省每天两小时"),
            opportunity_candidate("opportunity_2", "从这次发布看 AI Agent 的商业趋势", -5),
            opportunity_candidate("opportunity_3", "用一个生活比喻讲懂 Agent 工作流", -10),
        ],
    }
    created = client.post("/api/opportunities/analyze", json=analysis)
    assert created.status_code == 200, created.text
    opportunities = created.json()
    assert len(opportunities) == 3
    assert opportunities[0]["overall_score"] == 81
    assert opportunities[0]["exploration_bonus"] == 4
    assert opportunities[0]["learning_adjustment"] == 0
    assert opportunities[0]["knowledge_ids"] == ["knowledge_opportunity_fact", "knowledge_opportunity_inference"]
    assert len(client.get("/api/opportunities", params={"topic_id": "topic_opportunity"}).json()) == 3

    saved = client.patch("/api/opportunities/opportunity_1/status", json={"status": "saved"}).json()
    assert saved["status"] == "saved"
    rejected = client.patch("/api/opportunities/opportunity_2/status", json={"status": "rejected"}).json()
    assert rejected["status"] == "rejected"

    developed = client.post("/api/opportunities/opportunity_1/develop", json={}).json()
    assert developed["opportunity"]["status"] == "developed"
    assert developed["content"]["topic_id"] == "topic_opportunity"
    assert developed["content"]["raw"]["sourceOpportunityId"] == "opportunity_1"
    assert developed["content"]["raw"]["relevantKnowledgeIds"] == [
        "knowledge_opportunity_fact",
        "knowledge_opportunity_inference",
    ]
    retry = client.post("/api/opportunities/opportunity_1/develop", json={}).json()
    assert retry["content"]["id"] == developed["content"]["id"]
    assert len(client.get("/api/contents").json()) == 1

    actions = {item["action"] for item in client.get("/api/activity-logs", params={"limit": 500}).json()}
    assert {"opportunity_analyzed", "opportunity_saved", "opportunity_rejected", "opportunity_developed"} <= actions


def test_opportunity_workspace_and_reference_integrity(client):
    client.post("/api/topics", json={"id": "topic_default", "title": "Default", "category": "GPT"})
    client.post("/api/topics", json={"id": "topic_other_opportunity", "workspace_id": "other", "title": "Other"})
    client.post("/api/knowledge", json={
        "id": "knowledge_other_opportunity",
        "workspace_id": "other",
        "topic_id": "topic_other_opportunity",
        "title": "Other fact",
        "body": "Verified by an official source.",
        "knowledge_type": "Fact",
        "source": "Official",
        "source_url": "https://example.com/other",
    })
    client.post("/api/knowledge", json={
        "id": "knowledge_archived_opportunity",
        "topic_id": "topic_default",
        "title": "Archived source",
        "knowledge_type": "Source / Research",
        "status": "ARCHIVED",
    })
    candidates = [
        opportunity_candidate("invalid_1", "Angle one"),
        opportunity_candidate("invalid_2", "Angle two"),
        opportunity_candidate("invalid_3", "Angle three"),
    ]
    cross_topic = client.post("/api/opportunities/analyze", json={
        "workspace_id": "default",
        "topic_id": "topic_other_opportunity",
        "analysis_batch_id": "invalid_topic",
        "opportunities": candidates,
    })
    assert cross_topic.status_code == 409
    cross_knowledge = client.post("/api/opportunities/analyze", json={
        "topic_id": "topic_default",
        "analysis_batch_id": "invalid_knowledge",
        "knowledge_ids": ["knowledge_other_opportunity"],
        "opportunities": candidates,
    })
    assert cross_knowledge.status_code == 409
    archived_knowledge = client.post("/api/opportunities/analyze", json={
        "topic_id": "topic_default",
        "analysis_batch_id": "invalid_archived",
        "knowledge_ids": ["knowledge_archived_opportunity"],
        "opportunities": candidates,
    })
    assert archived_knowledge.status_code == 409
    assert client.get("/api/opportunities", params={"workspace_id": "default"}).json() == []


def create_performance_sample(client, suffix, platform, content_type, category, views, engagement, hook_style):
    topic_id = f"topic_learning_{suffix}"
    content_id = f"content_learning_{suffix}"
    version_id = f"version_learning_{suffix}"
    approval_id = f"approval_learning_{suffix}"
    job_id = f"job_learning_{suffix}"
    assert client.post("/api/topics", json={
        "id": topic_id,
        "title": f"Learning topic {suffix}",
        "category": category,
    }).status_code == 200
    assert client.post("/api/contents", json={
        "id": content_id,
        "topic_id": topic_id,
        "title": f"Learning content {suffix}",
        "platform": platform,
        "content_type": content_type,
        "source_url": f"https://example.com/source/{suffix}",
        "raw": {"draftTitle": f"Title {suffix}", "draftBody": "Body", "selectedAngle": "效率提升"},
    }).status_code == 200
    assert client.post("/api/platform-versions", json={
        "id": version_id,
        "content_id": content_id,
        "platform": platform,
        "content_type": content_type,
        "title": f"Title {suffix}",
        "hook": hook_style,
        "body": "Body",
        "raw": {"sourceUrl": f"https://example.com/source/{suffix}"},
    }).status_code == 200
    assert client.post("/api/approvals", json={
        "id": approval_id,
        "content_id": content_id,
        "platform_version_id": version_id,
        "status": "APPROVED",
        "approved_at": "2026-09-24T12:00:00Z",
    }).status_code == 200
    publish_payload = {
        "id": job_id,
        "content_id": content_id,
        "platform_version_id": version_id,
        "platform": platform,
        "content_type": content_type,
        "scheduled_at": f"2026-09-24T{10 + (int(suffix.split('_')[-1]) % 10):02d}:00",
        "status": "READY",
    }
    assert client.post("/api/publishing-tasks", json=publish_payload).status_code == 200
    assert client.put(f"/api/publishing-tasks/{job_id}", json={
        **publish_payload,
        "status": "PUBLISHED",
        "actual_published_at": "2026-09-24T12:05:00Z",
        "url": f"https://example.com/post/{suffix}",
    }).status_code == 200
    analytics = client.post(f"/api/publishing-tasks/{job_id}/tracking/start").json()
    likes = int(engagement * 0.45)
    saves = int(engagement * 0.30)
    shares = int(engagement * 0.15)
    comments = engagement - likes - saves - shares
    metrics = {
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "followersGained": max(0, int(engagement * 0.05)),
        "completionRate": 62 if engagement else 20,
    }
    assert client.post("/api/tracking-snapshots", json={
        "id": f"snapshot_learning_{suffix}",
        "publishing_task_id": job_id,
        "analytics_record_id": analytics["id"],
        "checkpoint_id": "7d",
        "label": "发布后 7 天",
        "status": "DONE",
        "metrics": metrics,
    }).status_code == 200
    assert client.post("/api/experience-records", json={
        "id": f"experience_learning_{suffix}",
        "content_id": content_id,
        "topic_id": topic_id,
        "platform_version_id": version_id,
        "publishing_task_id": job_id,
        "analytics_record_id": analytics["id"],
        "platform": platform,
        "content_type": content_type,
        "topic_category": category,
        "performance_result": "tracked",
        "raw": {"hookStyle": hook_style, "sourceMetrics": metrics},
    }).status_code == 200
    return {"topic_id": topic_id, "content_id": content_id, "analytics_id": analytics["id"]}


def test_creator_intelligence_learning_lifecycle_and_integrations(client):
    assert client.put("/api/creator-memory", json={
        "account_positioning": "面向中文创作者的 AI 工作流账号",
        "target_audience": "独立创作者",
        "content_pillars": ["AI Agent", "AI Coding", "AI Video"],
        "preferred_formats": ["长文"],
        "platform_preferences": ["小红书"],
    }).status_code == 200

    # Deterministic evidence: one proven platform/format pattern plus genuine counter-examples.
    for index in range(3):
        create_performance_sample(client, f"high_{index}", "抖音", "口播稿", "AI Agent", 1000, 200, "问题式 Hook")
        create_performance_sample(client, f"low_format_{index}", "抖音", "短帖", "AI Coding", 1000, 5, "平铺 Hook")
        create_performance_sample(client, f"low_platform_{index}", "B站", "长文", "AI Video", 1000, 10, "叙事 Hook")

    generated = client.post("/api/creator-intelligence/generate", json={"workspace_id": "default"})
    assert generated.status_code == 200, generated.text
    intelligence = generated.json()
    platform_learning = next(item for item in intelligence["learnings"] if item["pattern_key"] == "platform:all:抖音")
    format_learning = next(item for item in intelligence["learnings"] if item["pattern_key"] == "format:抖音:口播稿")
    assert platform_learning["status"] == "active"
    assert format_learning["status"] == "active"
    assert platform_learning["sample_size"] == 6
    assert len(platform_learning["evidence"]) == 6
    assert platform_learning["confidence"] >= 60
    initial_confidence = platform_learning["confidence"]

    learning_knowledge = client.get("/api/knowledge", params={"type": "Learning"}).json()
    assert any(item["raw"].get("creatorLearningId") == platform_learning["id"] for item in learning_knowledge)
    assert all(item["knowledge_type"] == "Learning" for item in learning_knowledge)

    suggestions = [item for item in intelligence["strategy_suggestions"] if item["status"] == "pending"]
    platform_suggestion = next(item for item in suggestions if item["proposed_change"].get("field") == "platformPreferences")
    format_suggestion = next(item for item in suggestions if item["proposed_change"].get("field") == "preferredFormats")
    accepted = client.patch(f"/api/strategy-suggestions/{platform_suggestion['id']}", json={"workspace_id": "default", "decision": "accepted"})
    assert accepted.status_code == 200
    assert "抖音" in accepted.json()["creator_memory"]["platform_preferences"]
    rejected = client.patch(f"/api/strategy-suggestions/{format_suggestion['id']}", json={"workspace_id": "default", "decision": "rejected"})
    assert rejected.status_code == 200
    assert "口播稿" not in rejected.json()["creator_memory"]["preferred_formats"]

    local_intelligence_payload = {
        "creatorLearnings": [platform_learning],
        "strategySuggestions": [platform_suggestion],
    }
    first_import = client.post("/api/import/localstorage-business", json=local_intelligence_payload).json()
    second_import = client.post("/api/import/localstorage-business", json=local_intelligence_payload).json()
    assert first_import["creator_learnings"]["updated"] == 1
    assert first_import["strategy_suggestions"]["updated"] == 1
    assert second_import["creator_learnings"]["skipped"] == 1
    assert second_import["strategy_suggestions"]["skipped"] == 1

    topic = client.post("/api/topics", json={
        "id": "topic_learning_opportunity",
        "title": "AI Agent workflow for creators",
        "category": "AI Agent",
        "raw": {"tags": ["Agent", "Creator"]},
    }).json()
    context = client.get(f"/api/topics/{topic['id']}/opportunity-context").json()
    assert platform_learning["id"] in {item["id"] for item in context["learnings"]}
    analyzed = client.post("/api/opportunities/analyze", json={
        "topic_id": topic["id"],
        "analysis_batch_id": "learning_integration_batch",
        "opportunities": [
            opportunity_candidate("learning_opportunity_1", "AI Agent 如何帮助创作者提升效率"),
            opportunity_candidate("learning_opportunity_2", "AI Agent 工作流的真实边界"),
            opportunity_candidate("learning_opportunity_3", "普通创作者应该测试哪些 Agent"),
        ],
    }).json()
    assert analyzed[0]["learning_adjustment"] > 0
    assert analyzed[0]["learning_ids"]
    assert any("Confidence" in line for line in analyzed[0]["learning_explanation"])
    developed = client.post(f"/api/opportunities/{analyzed[0]['id']}/develop", json={}).json()
    assert developed["content"]["raw"]["relevantLearningIds"] == analyzed[0]["learning_ids"]
    assert developed["content"]["raw"]["learningGuidance"] == analyzed[0]["learning_explanation"]

    # More consistent supporting data must not lower confidence.
    create_performance_sample(client, "high_3", "抖音", "口播稿", "AI Agent", 1000, 210, "问题式 Hook")
    refreshed = client.post("/api/creator-intelligence/generate", json={"workspace_id": "default"}).json()
    refreshed_platform = next(item for item in refreshed["learnings"] if item["id"] == platform_learning["id"])
    assert refreshed_platform["sample_size"] == 7
    assert refreshed_platform["confidence"] >= initial_confidence

    # Conflicting outcomes weaken, rather than silently preserving, a prior active rule.
    for index in range(4, 10):
        create_performance_sample(client, f"conflict_{index}", "抖音", "口播稿", "AI Agent", 1000, 0, "问题式 Hook")
    conflicted = client.post("/api/creator-intelligence/generate", json={"workspace_id": "default"}).json()
    weakened = next(item for item in conflicted["learnings"] if item["id"] == platform_learning["id"])
    assert weakened["status"] == "weakened"
    assert weakened["sample_size"] == 13

    actions = {item["action"] for item in client.get("/api/activity-logs", params={"limit": 500}).json()}
    assert {"learning_generated", "learning_validated", "learning_weakened", "strategy_suggestion_created", "strategy_suggestion_accepted", "strategy_suggestion_rejected"} <= actions

    assert client.post(f"/api/creator-learnings/{platform_learning['id']}/archive", params={"workspace_id": "other"}).status_code == 409
    assert client.patch(f"/api/strategy-suggestions/{platform_suggestion['id']}", json={"workspace_id": "other", "decision": "accepted"}).status_code == 409
