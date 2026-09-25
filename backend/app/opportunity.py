"""Opportunity Discovery business rules.

AI may suggest angles and dimension scores, but this module owns references,
status transitions, deterministic scoring, idempotency, and Content development.
"""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .activity import log_activity
from .models import Content, ContentOpportunity, CreatorProfile, KnowledgeEntry, Topic
from .workflow import DEFAULT_WORKSPACE_ID, WorkflowConflict, ensure_owned, ensure_workspace, save_content, stable_hash


OPPORTUNITY_STATUSES = {"candidate", "saved", "rejected", "developed"}
OPPORTUNITY_WEIGHTS = {
    "novelty": 0.15,
    "timeliness": 0.15,
    "audience_fit": 0.15,
    "creator_fit": 0.15,
    "human_need_strength": 0.15,
    "platform_fit_score": 0.10,
    "visual_potential": 0.10,
    "production_ease": 0.05,
}
STATUS_TRANSITIONS = {
    "candidate": {"candidate", "saved", "rejected"},
    "saved": {"candidate", "saved", "rejected"},
    "rejected": {"candidate", "saved", "rejected"},
    "developed": {"developed"},
}


def clamp_score(value: Any) -> int:
    try:
        return max(0, min(100, int(round(float(value or 0)))))
    except (TypeError, ValueError):
        return 0


def calculate_opportunity_score(values: dict[str, Any]) -> int:
    production_ease = 100 - clamp_score(values.get("production_difficulty"))
    weighted = (
        clamp_score(values.get("novelty")) * OPPORTUNITY_WEIGHTS["novelty"]
        + clamp_score(values.get("timeliness")) * OPPORTUNITY_WEIGHTS["timeliness"]
        + clamp_score(values.get("audience_fit")) * OPPORTUNITY_WEIGHTS["audience_fit"]
        + clamp_score(values.get("creator_fit")) * OPPORTUNITY_WEIGHTS["creator_fit"]
        + clamp_score(values.get("human_need_strength")) * OPPORTUNITY_WEIGHTS["human_need_strength"]
        + clamp_score(values.get("platform_fit_score")) * OPPORTUNITY_WEIGHTS["platform_fit_score"]
        + clamp_score(values.get("visual_potential")) * OPPORTUNITY_WEIGHTS["visual_potential"]
        + production_ease * OPPORTUNITY_WEIGHTS["production_ease"]
    )
    return clamp_score(weighted)


def opportunity_angle_key(values: dict[str, Any]) -> str:
    return stable_hash({
        "contentOpportunity": values.get("content_opportunity") or "",
        "recommendedFormat": values.get("recommended_format") or "",
        "platformFit": sorted(values.get("platform_fit") or []),
    })


def ensure_creator_profile(db: Session, workspace_id: str, creator_profile_id: str | None = None) -> CreatorProfile:
    if creator_profile_id:
        creator = db.get(CreatorProfile, creator_profile_id)
        if creator is not None:
            ensure_owned(creator, workspace_id, "CreatorProfile")
            return creator
        expected_id = "default" if workspace_id == DEFAULT_WORKSPACE_ID else f"creator_{stable_hash(workspace_id)[:20]}"
        if creator_profile_id != expected_id:
            raise WorkflowConflict("CreatorProfile not found in workspace")
        creator = CreatorProfile(id=expected_id, workspace_id=workspace_id)
        db.add(creator)
        db.flush()
        return creator
    creator = db.scalar(select(CreatorProfile).where(CreatorProfile.workspace_id == workspace_id))
    if creator is None:
        creator = CreatorProfile(
            id="default" if workspace_id == DEFAULT_WORKSPACE_ID else f"creator_{stable_hash(workspace_id)[:20]}",
            workspace_id=workspace_id,
        )
        db.add(creator)
        db.flush()
    return creator


def validate_knowledge_ids(db: Session, workspace_id: str, knowledge_ids: list[str]) -> list[KnowledgeEntry]:
    result: list[KnowledgeEntry] = []
    for knowledge_id in dict.fromkeys(knowledge_ids):
        item = db.get(KnowledgeEntry, knowledge_id)
        ensure_owned(item, workspace_id, "KnowledgeEntry")
        if item.status != "ACTIVE":
            raise WorkflowConflict("Archived or draft Knowledge cannot ground an Opportunity")
        result.append(item)
    return result


def _search_terms(topic: Topic) -> set[str]:
    raw = topic.raw or {}
    source = " ".join([
        topic.title or "",
        topic.category or "",
        " ".join(str(value) for value in (raw.get("tags") or [])),
    ]).casefold()
    return {token for token in re.findall(r"[\w\u4e00-\u9fff-]+", source) if len(token) > 1}


def retrieve_opportunity_context(db: Session, topic_id: str, workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = 12) -> tuple[Topic, list[KnowledgeEntry], CreatorProfile]:
    topic = db.get(Topic, topic_id)
    ensure_owned(topic, workspace_id, "Topic")
    creator = ensure_creator_profile(db, workspace_id)
    terms = _search_terms(topic)
    candidates = list(db.scalars(select(KnowledgeEntry).where(
        KnowledgeEntry.workspace_id == workspace_id,
        KnowledgeEntry.status == "ACTIVE",
    )).all())

    ranked: list[tuple[int, KnowledgeEntry]] = []
    for item in candidates:
        relevance = 0
        if item.topic_id == topic.id:
            relevance += 120
        if item.content_id:
            linked_content = db.get(Content, item.content_id)
            if linked_content and linked_content.topic_id == topic.id:
                relevance += 90
        item_text = " ".join([
            item.title or "",
            item.body or "",
            item.source or "",
            " ".join(str(value) for value in (item.tags or [])),
        ]).casefold()
        relevance += min(60, sum(12 for term in terms if term in item_text))
        if item.knowledge_type in {"Creator Preference", "Learning", "Playbook"} and relevance:
            relevance += 10
        if relevance:
            ranked.append((relevance + int(item.confidence or 0) // 10, item))
    ranked.sort(key=lambda pair: (pair[0], pair[1].confidence, pair[1].updated_at), reverse=True)
    return topic, [item for _, item in ranked[: max(1, min(limit, 30))]], creator


def _candidate_values(candidate: dict[str, Any], *, workspace_id: str, topic: Topic, creator: CreatorProfile, batch_id: str) -> dict[str, Any]:
    values = {
        **candidate,
        "workspace_id": workspace_id,
        "topic_id": topic.id,
        "creator_profile_id": creator.id,
        "analysis_batch_id": batch_id,
        "angle_key": opportunity_angle_key(candidate),
        "status": "candidate",
        "developed_content_id": None,
    }
    for key in (
        "novelty",
        "timeliness",
        "audience_fit",
        "creator_fit",
        "human_need_strength",
        "platform_fit_score",
        "visual_potential",
        "production_difficulty",
    ):
        values[key] = clamp_score(values.get(key))
    values["overall_score"] = calculate_opportunity_score(values)
    values["raw"] = {
        **(values.get("raw") or {}),
        "scoreWeights": OPPORTUNITY_WEIGHTS,
        "productionEase": 100 - values["production_difficulty"],
    }
    return values


def analyze_opportunities(
    db: Session,
    *,
    workspace_id: str,
    topic_id: str,
    creator_profile_id: str | None,
    analysis_batch_id: str,
    knowledge_ids: list[str],
    candidates: list[dict[str, Any]],
) -> list[ContentOpportunity]:
    ensure_workspace(db, workspace_id)
    topic = db.get(Topic, topic_id)
    ensure_owned(topic, workspace_id, "Topic")
    creator = ensure_creator_profile(db, workspace_id, creator_profile_id)
    knowledge = validate_knowledge_ids(db, workspace_id, knowledge_ids)
    if not 3 <= len(candidates) <= 5:
        raise WorkflowConflict("Opportunity analysis must contain 3 to 5 angles")
    candidate_ids = [str(candidate.get("id") or "") for candidate in candidates]
    angle_keys = [opportunity_angle_key(candidate) for candidate in candidates]
    if "" in candidate_ids or len(set(candidate_ids)) != len(candidate_ids) or len(set(angle_keys)) != len(angle_keys):
        raise WorkflowConflict("Opportunity analysis must contain unique angle ids and ideas")

    results: list[ContentOpportunity] = []
    for candidate in candidates:
        values = _candidate_values(candidate, workspace_id=workspace_id, topic=topic, creator=creator, batch_id=analysis_batch_id)
        existing = db.get(ContentOpportunity, candidate["id"])
        same_angle = db.scalar(select(ContentOpportunity).where(
            ContentOpportunity.workspace_id == workspace_id,
            ContentOpportunity.topic_id == topic.id,
            ContentOpportunity.analysis_batch_id == analysis_batch_id,
            ContentOpportunity.angle_key == values["angle_key"],
        ))
        if existing:
            ensure_owned(existing, workspace_id, "ContentOpportunity")
            if existing.topic_id != topic.id or existing.analysis_batch_id != analysis_batch_id:
                raise WorkflowConflict("Opportunity id belongs to another analysis")
            item = existing
        elif same_angle:
            item = same_angle
        else:
            item = ContentOpportunity(id=candidate["id"], **{key: value for key, value in values.items() if key != "id"})
            item.relevant_knowledge = knowledge
            db.add(item)
        results.append(item)

    db.flush()
    log_activity(
        db,
        "opportunity_analyzed",
        "Topic",
        topic.id,
        {
            "analysisBatchId": analysis_batch_id,
            "opportunityIds": [item.id for item in results],
            "knowledgeIds": [item.id for item in knowledge],
            "creatorProfileId": creator.id,
        },
        workspace_id=workspace_id,
    )
    db.commit()
    for item in results:
        db.refresh(item)
    return results


def update_opportunity_status(db: Session, opportunity_id: str, workspace_id: str, status: str) -> ContentOpportunity:
    item = db.scalar(select(ContentOpportunity).where(ContentOpportunity.id == opportunity_id).with_for_update())
    ensure_owned(item, workspace_id, "ContentOpportunity")
    if status not in OPPORTUNITY_STATUSES - {"developed"}:
        raise WorkflowConflict("Unsupported Opportunity status")
    if status not in STATUS_TRANSITIONS[item.status]:
        raise WorkflowConflict(f"Illegal Opportunity transition: {item.status} -> {status}")
    if item.status == status:
        return item
    item.status = status
    action = "opportunity_saved" if status == "saved" else "opportunity_rejected" if status == "rejected" else "opportunity_restored"
    log_activity(db, action, "ContentOpportunity", item.id, {"topicId": item.topic_id}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    return item


def _studio_format(value: str) -> str:
    text = (value or "").casefold()
    if "长" in text or "b站" in text or "深度" in text:
        return "长文"
    if "口播" in text or "视频" in text or "脚本" in text:
        return "口播稿"
    return "短帖"


def develop_opportunity(db: Session, opportunity_id: str, workspace_id: str, content_id: str | None = None) -> tuple[ContentOpportunity, Content]:
    item = db.scalar(select(ContentOpportunity).where(ContentOpportunity.id == opportunity_id).with_for_update())
    ensure_owned(item, workspace_id, "ContentOpportunity")
    if item.developed_content_id:
        content = db.get(Content, item.developed_content_id)
        ensure_owned(content, workspace_id, "Content")
        return item, content
    if item.status == "rejected":
        raise WorkflowConflict("Rejected Opportunity must be restored before Develop")
    topic = db.get(Topic, item.topic_id)
    ensure_owned(topic, workspace_id, "Topic")
    chosen_platform = next((value for value in item.platform_fit if value in {"小红书", "抖音", "B站", "公众号"}), "小红书")
    target_content_id = content_id or f"content_opportunity_{stable_hash(item.id)[:24]}"
    raw = {
        "sourceOpportunityId": item.id,
        "sourceTopicId": topic.id,
        "sourcePlatform": topic.source,
        "sourceTitle": topic.title,
        "sourceUrl": topic.url,
        "sourceAuthor": topic.author,
        "sourcePublishedAt": (topic.raw or {}).get("publishedAt") or "",
        "originalSummary": item.summary or (topic.raw or {}).get("summary") or "",
        "topic": topic.category,
        "tags": list(dict.fromkeys([*(topic.raw or {}).get("tags", []), "Opportunity"])),
        "selectedAngle": item.content_opportunity,
        "recommendedAngle": item.content_opportunity,
        "recommendationReason": item.reasoning,
        "targetPlatforms": item.platform_fit,
        "studioPlatform": chosen_platform,
        "studioFormat": _studio_format(item.recommended_format),
        "finalScore": item.overall_score,
        "hotScore": item.timeliness,
        "chinaFitScore": item.audience_fit,
        "opportunityScore": item.overall_score,
        "opportunityReasoning": item.reasoning,
        "relevantKnowledgeIds": item.knowledge_ids,
        "creatorProfileId": item.creator_profile_id,
    }
    content = save_content(db, target_content_id, {
        "workspace_id": workspace_id,
        "topic_id": topic.id,
        "title": item.content_opportunity,
        "status": "DRAFT",
        "platform": chosen_platform,
        "content_type": _studio_format(item.recommended_format),
        "source_url": topic.url,
        "raw": raw,
    }, commit=False)
    item.developed_content_id = content.id
    item.status = "developed"
    log_activity(
        db,
        "opportunity_developed",
        "ContentOpportunity",
        item.id,
        {"topicId": topic.id, "contentId": content.id},
        workspace_id=workspace_id,
    )
    db.commit()
    db.refresh(item)
    db.refresh(content)
    return item, content


def import_opportunity_record(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> ContentOpportunity:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    ensure_workspace(db, workspace_id)
    topic = db.get(Topic, values.get("topic_id"))
    ensure_owned(topic, workspace_id, "Topic")
    creator = ensure_creator_profile(db, workspace_id, values.get("creator_profile_id"))
    knowledge = validate_knowledge_ids(db, workspace_id, values.get("knowledge_ids") or [])
    status = str(values.get("status") or "candidate").casefold()
    if status not in OPPORTUNITY_STATUSES:
        status = "candidate"
    developed_content_id = values.get("developed_content_id")
    if developed_content_id:
        ensure_owned(db.get(Content, developed_content_id), workspace_id, "Content")
    elif status == "developed":
        status = "saved"
    candidate_values = _candidate_values(values, workspace_id=workspace_id, topic=topic, creator=creator, batch_id=values.get("analysis_batch_id") or f"import_{topic.id}")
    candidate_values.update({
        "status": status,
        "developed_content_id": developed_content_id,
        "angle_key": values.get("angle_key") or candidate_values["angle_key"],
    })
    candidate_values.pop("knowledge_ids", None)
    existing = db.get(ContentOpportunity, record_id)
    if existing:
        ensure_owned(existing, workspace_id, "ContentOpportunity")
        for key, value in candidate_values.items():
            if key != "id":
                setattr(existing, key, value)
        item = existing
    else:
        same = db.scalar(select(ContentOpportunity).where(
            ContentOpportunity.workspace_id == workspace_id,
            ContentOpportunity.topic_id == topic.id,
            ContentOpportunity.analysis_batch_id == candidate_values["analysis_batch_id"],
            ContentOpportunity.angle_key == candidate_values["angle_key"],
        ))
        item = same or ContentOpportunity(id=record_id, **candidate_values)
        if same is None:
            db.add(item)
    item.relevant_knowledge = knowledge
    db.flush()
    if commit:
        db.commit()
        db.refresh(item)
    return item
