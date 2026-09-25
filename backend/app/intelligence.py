"""Deterministic Creator Intelligence and evidence-backed learning lifecycle."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .activity import log_activity
from .models import (
    AnalyticsRecord,
    Content,
    ContentOpportunity,
    CreatorLearning,
    CreatorLearningEvidence,
    CreatorProfile,
    ExperienceRecord,
    KnowledgeEntry,
    PublishingTask,
    StrategySuggestion,
    Topic,
    TrackingSnapshot,
)
from .workflow import DEFAULT_WORKSPACE_ID, WorkflowConflict, canonical_status, ensure_owned, ensure_workspace, stable_hash


LEARNING_STATUSES = {"proposed", "active", "weakened", "archived"}
STRATEGY_STATUSES = {"pending", "accepted", "rejected", "ignored"}
STRATEGY_LIST_FIELDS = {
    "contentPillars": "content_pillars",
    "preferredFormats": "preferred_formats",
    "platformPreferences": "platform_preferences",
    "topicsToAvoid": "topics_to_avoid",
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def clamp(value: Any, low: int = 0, high: int = 100) -> int:
    try:
        return max(low, min(high, int(round(float(value or 0)))))
    except (TypeError, ValueError):
        return low


def rate(numerator: int, denominator: int) -> float:
    return round((numerator / denominator * 100), 4) if denominator else 0.0


def parse_datetime(value: Any, fallback: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return fallback or utcnow()


def ensure_creator(db: Session, workspace_id: str) -> CreatorProfile:
    ensure_workspace(db, workspace_id)
    creator = db.scalar(select(CreatorProfile).where(CreatorProfile.workspace_id == workspace_id))
    if creator is None:
        creator = CreatorProfile(
            id="default" if workspace_id == DEFAULT_WORKSPACE_ID else f"creator_{stable_hash(workspace_id)[:20]}",
            workspace_id=workspace_id,
        )
        db.add(creator)
        db.flush()
    return creator


def analytics_metrics(record: AnalyticsRecord, latest_snapshot: TrackingSnapshot | None = None) -> dict[str, Any]:
    source = latest_snapshot.metrics if latest_snapshot else (record.raw or {})
    views = max(0, int(record.views or source.get("views") or 0))
    likes = max(0, int(record.likes or source.get("likes") or 0))
    comments = max(0, int(record.comments or source.get("comments") or 0))
    shares = max(0, int(record.shares or source.get("shares") or 0))
    saves = max(0, int(record.saves or source.get("saves") or 0))
    followers = max(0, int(record.followers_gained or source.get("followersGained") or source.get("followers_gained") or 0))
    engagement = likes + comments + shares + saves
    completion = float(source.get("completionRate") or source.get("completion_rate") or source.get("retention") or 0)
    return {
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "followersGained": followers,
        "engagementRate": rate(engagement, views),
        "saveRate": rate(saves, views),
        "shareRate": rate(shares, views),
        "commentRate": rate(comments, views),
        "followConversion": rate(followers, views),
        "completionRate": round(completion, 4),
    }


def performance_rows(db: Session, workspace_id: str) -> list[dict[str, Any]]:
    analytics_records = list(db.scalars(select(AnalyticsRecord).where(AnalyticsRecord.workspace_id == workspace_id)).all())
    snapshots = list(db.scalars(select(TrackingSnapshot).where(TrackingSnapshot.workspace_id == workspace_id)).all())
    experiences = list(db.scalars(select(ExperienceRecord).where(ExperienceRecord.workspace_id == workspace_id)).all())
    latest_snapshot: dict[str, TrackingSnapshot] = {}
    snapshot_ids: dict[str, list[str]] = defaultdict(list)
    for snapshot in snapshots:
        if canonical_status(snapshot.status) != "DONE":
            continue
        snapshot_ids[snapshot.analytics_record_id or ""].append(snapshot.id)
        prior = latest_snapshot.get(snapshot.analytics_record_id or "")
        if prior is None or (snapshot.recorded_at, snapshot.sequence) > (prior.recorded_at, prior.sequence):
            latest_snapshot[snapshot.analytics_record_id or ""] = snapshot
    experience_by_analytics = {item.analytics_record_id: item for item in experiences if item.analytics_record_id}

    rows: list[dict[str, Any]] = []
    for record in analytics_records:
        job = db.get(PublishingTask, record.publishing_task_id) if record.publishing_task_id else None
        if job is None or canonical_status(job.status) != "PUBLISHED":
            continue
        content = db.get(Content, record.content_id or job.content_id)
        if content is None or content.workspace_id != workspace_id:
            continue
        experience = experience_by_analytics.get(record.id)
        topic = db.get(Topic, content.topic_id) if content.topic_id else None
        opportunity_id = (content.raw or {}).get("sourceOpportunityId") or None
        opportunity = db.get(ContentOpportunity, opportunity_id) if opportunity_id else None
        if opportunity and opportunity.workspace_id != workspace_id:
            opportunity = None
            opportunity_id = None
        metrics = analytics_metrics(record, latest_snapshot.get(record.id))
        if metrics["views"] <= 0:
            continue
        observed_at = parse_datetime(
            (latest_snapshot.get(record.id).recorded_at if latest_snapshot.get(record.id) else None)
            or record.stats_date,
            record.updated_at,
        )
        experience_raw = (experience.raw if experience else {}) or {}
        rows.append({
            "analytics": record,
            "job": job,
            "content": content,
            "topic": topic,
            "opportunity": opportunity,
            "experience": experience,
            "metrics": metrics,
            "observed_at": observed_at,
            "tracking_snapshot_ids": snapshot_ids.get(record.id, []),
            "platform": record.platform or job.platform,
            "format": record.content_type or job.content_type,
            "topic_pillar": (experience.topic_category if experience else "") or (topic.category if topic else "") or (content.raw or {}).get("topic") or "",
            "hook": experience_raw.get("hookStyle") or (content.raw or {}).get("hookStyle") or "",
            "angle": (opportunity.content_opportunity if opportunity else "") or (content.raw or {}).get("selectedAngle") or "",
        })
    return rows


def confidence_components(sample_size: int, consistency: int, recency_score: int, effect_strength: int) -> int:
    sample_component = min(40, sample_size * 8)
    confidence = round(sample_component + consistency * 0.25 + recency_score * 0.20 + effect_strength * 0.15)
    if sample_size == 1:
        confidence = min(confidence, 35)
    elif sample_size == 2:
        confidence = min(confidence, 48)
    return clamp(confidence)


def pattern_statement(learning_type: str, context: str, direction: str, metrics: dict[str, Any]) -> str:
    label = {"platform": "平台", "format": "内容形式", "topic_pillar": "Content Pillar", "hook": "Hook 风格", "angle": "内容角度"}.get(learning_type, learning_type)
    relation = "表现高于当前基线" if direction == "positive" else "表现低于当前基线" if direction == "negative" else "目前与基线差异不明确"
    return f"{label}「{context}」{relation}（平均互动率 {metrics['avgEngagementRate']}%，样本 {metrics['sampleSize']}）。"


def build_pattern_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []
    global_avg = sum(row["metrics"]["engagementRate"] for row in rows) / len(rows)
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["platform"]:
            groups[("platform", row["platform"], "all")].append(row)
        for learning_type, key in (("format", "format"), ("topic_pillar", "topic_pillar"), ("hook", "hook"), ("angle", "angle")):
            if row[key]:
                groups[(learning_type, row[key], row["platform"] or "all")].append(row)

    candidates: list[dict[str, Any]] = []
    for (learning_type, context, platform_context), members in groups.items():
        peers = rows if learning_type == "platform" else [row for row in rows if (row["platform"] or "all") == platform_context]
        baseline = sum(row["metrics"]["engagementRate"] for row in peers) / len(peers) if peers else global_avg
        avg_er = sum(row["metrics"]["engagementRate"] for row in members) / len(members)
        relative = ((avg_er - baseline) / max(abs(baseline), 0.1)) * 100
        direction = "positive" if relative >= 5 else "negative" if relative <= -5 else "neutral"
        if direction == "positive":
            supporting = [row for row in members if row["metrics"]["engagementRate"] >= baseline]
        elif direction == "negative":
            supporting = [row for row in members if row["metrics"]["engagementRate"] <= baseline]
        else:
            supporting = [row for row in members if abs(row["metrics"]["engagementRate"] - baseline) <= max(0.5, baseline * 0.15)]
        consistency = clamp(len(supporting) / len(members) * 100)
        latest = max(row["observed_at"] for row in members)
        days_old = max(0, (utcnow() - latest).days)
        recency_score = clamp(100 - days_old * 2)
        effect_strength = clamp(abs(relative))
        sample_size = len(members)
        confidence = confidence_components(sample_size, consistency, recency_score, effect_strength)
        metrics = {
            "sampleSize": sample_size,
            "avgViews": round(sum(row["metrics"]["views"] for row in members) / sample_size, 2),
            "avgEngagementRate": round(avg_er, 2),
            "avgSaveRate": round(sum(row["metrics"]["saveRate"] for row in members) / sample_size, 2),
            "avgShareRate": round(sum(row["metrics"]["shareRate"] for row in members) / sample_size, 2),
            "avgCommentRate": round(sum(row["metrics"]["commentRate"] for row in members) / sample_size, 2),
            "avgFollowConversion": round(sum(row["metrics"]["followConversion"] for row in members) / sample_size, 2),
            "avgCompletionRate": round(sum(row["metrics"]["completionRate"] for row in members) / sample_size, 2),
            "baselineEngagementRate": round(baseline, 2),
            "relativeDifferencePercent": round(relative, 2),
            "platformContext": platform_context,
        }
        pattern_key = f"{learning_type}:{platform_context}:{context}".casefold()
        candidates.append({
            "pattern_key": pattern_key,
            "learning_type": learning_type,
            "context_key": context,
            "direction": direction,
            "supporting_metrics": metrics,
            "sample_size": sample_size,
            "confidence": confidence,
            "consistency": consistency,
            "recency_score": recency_score,
            "effect_strength": effect_strength,
            "last_validated_at": utcnow(),
            "learning_statement": pattern_statement(learning_type, context, direction, metrics),
            "rows": members,
            "baseline": baseline,
        })
    return candidates


def next_learning_status(existing: CreatorLearning | None, candidate: dict[str, Any]) -> str:
    if existing and existing.status == "archived":
        return "archived"
    direction_changed = bool(existing and existing.direction not in {"neutral", candidate["direction"]} and candidate["direction"] != "neutral")
    contradicted = candidate["consistency"] < 50 or candidate["confidence"] < 45
    if existing and existing.status == "active" and (direction_changed or contradicted):
        return "weakened"
    if existing and existing.status == "weakened":
        if candidate["sample_size"] >= 3 and candidate["confidence"] >= 65 and candidate["consistency"] >= 65 and not direction_changed:
            return "active"
        return "weakened"
    if candidate["sample_size"] >= 3 and candidate["confidence"] >= 60 and candidate["direction"] != "neutral":
        return "active"
    return "proposed"


def sync_learning_knowledge(db: Session, learning: CreatorLearning) -> None:
    knowledge_id = learning.knowledge_entry_id or f"knowledge_learning_{stable_hash(learning.id)[:24]}"
    status = "ARCHIVED" if learning.status == "archived" else "ACTIVE" if learning.status == "active" else "DRAFT"
    evidence_ids = list(db.scalars(select(CreatorLearningEvidence.id).where(CreatorLearningEvidence.learning_id == learning.id)).all())
    values = {
        "workspace_id": learning.workspace_id,
        "title": f"Creator Learning · {learning.context_key}",
        "body": learning.learning_statement,
        "knowledge_type": "Learning",
        "source": "Creator Intelligence",
        "source_url": "",
        "tags": [learning.learning_type, learning.status, learning.direction],
        "confidence": learning.confidence,
        "status": status,
        "raw": {
            "creatorLearningId": learning.id,
            "patternKey": learning.pattern_key,
            "evidenceIds": evidence_ids,
            "supportingMetrics": learning.supporting_metrics,
            "sampleSize": learning.sample_size,
            "lastValidatedAt": learning.last_validated_at.isoformat() if learning.last_validated_at else "",
        },
    }
    item = db.get(KnowledgeEntry, knowledge_id)
    created = item is None
    if item is None:
        item = KnowledgeEntry(id=knowledge_id, **values)
        db.add(item)
    else:
        ensure_owned(item, learning.workspace_id, "KnowledgeEntry")
        for key, value in values.items():
            setattr(item, key, value)
    learning.knowledge_entry_id = knowledge_id
    log_activity(
        db,
        "knowledge_created" if created else "knowledge_updated",
        "KnowledgeEntry",
        knowledge_id,
        {"source": "CreatorLearning", "learningId": learning.id},
        workspace_id=learning.workspace_id,
    )


def upsert_learning_evidence(db: Session, learning: CreatorLearning, candidate: dict[str, Any]) -> None:
    baseline = candidate["baseline"]
    direction = candidate["direction"]
    for row in candidate["rows"]:
        analytics = row["analytics"]
        evidence = db.scalar(select(CreatorLearningEvidence).where(
            CreatorLearningEvidence.learning_id == learning.id,
            CreatorLearningEvidence.analytics_record_id == analytics.id,
        ))
        delta = ((row["metrics"]["engagementRate"] - baseline) / max(abs(baseline), 0.1)) * 100
        supports = delta >= 0 if direction == "positive" else delta <= 0 if direction == "negative" else abs(delta) <= 15
        values = {
            "workspace_id": learning.workspace_id,
            "learning_id": learning.id,
            "content_id": row["content"].id,
            "opportunity_id": row["opportunity"].id if row["opportunity"] else None,
            "publishing_task_id": row["job"].id,
            "analytics_record_id": analytics.id,
            "experience_record_id": row["experience"].id if row["experience"] else None,
            "tracking_snapshot_ids": row["tracking_snapshot_ids"],
            "metrics": row["metrics"],
            "observed_at": row["observed_at"],
            "supports": supports,
            "outcome_score": clamp(delta, -100, 100),
            "raw": {"baselineEngagementRate": round(baseline, 4), "direction": direction},
        }
        if evidence is None:
            evidence = CreatorLearningEvidence(id=f"evidence_{stable_hash(f'{learning.id}|{analytics.id}')[:28]}", **values)
            db.add(evidence)
        else:
            for key, value in values.items():
                setattr(evidence, key, value)


def generate_strategy_suggestions(db: Session, creator: CreatorProfile, learnings: list[CreatorLearning]) -> list[StrategySuggestion]:
    created: list[StrategySuggestion] = []
    field_map = {
        "platform": ("platformPreferences", creator.platform_preferences, "平台偏好"),
        "format": ("preferredFormats", creator.preferred_formats, "内容形式偏好"),
        "topic_pillar": ("contentPillars", creator.content_pillars, "Content Pillar"),
    }
    for learning in learnings:
        if learning.status != "active" or learning.direction != "positive" or learning.confidence < 65 or learning.sample_size < 3:
            continue
        mapping = field_map.get(learning.learning_type)
        if not mapping:
            continue
        field, current_values, label = mapping
        if learning.context_key in (current_values or []):
            continue
        change = {"field": field, "action": "add", "value": learning.context_key}
        fingerprint = stable_hash({"workspace": learning.workspace_id, "change": change})
        existing = db.scalar(select(StrategySuggestion).where(
            StrategySuggestion.workspace_id == learning.workspace_id,
            StrategySuggestion.fingerprint == fingerprint,
        ))
        if existing:
            continue
        item = StrategySuggestion(
            id=f"strategy_{fingerprint[:24]}",
            workspace_id=learning.workspace_id,
            creator_profile_id=creator.id,
            fingerprint=fingerprint,
            suggestion_type=field,
            statement=f"建议把「{learning.context_key}」加入{label}。",
            proposed_change=change,
            rationale=f"{learning.learning_statement} Confidence {learning.confidence}，样本 {learning.sample_size}。",
            supporting_learning_ids=[learning.id],
            status="pending",
            raw={"humanApprovalRequired": True},
        )
        db.add(item)
        log_activity(db, "strategy_suggestion_created", "StrategySuggestion", item.id, {"learningIds": [learning.id]}, workspace_id=learning.workspace_id)
        created.append(item)
    return created


def generate_creator_intelligence(db: Session, workspace_id: str = DEFAULT_WORKSPACE_ID) -> tuple[list[CreatorLearning], list[StrategySuggestion], dict[str, Any]]:
    creator = ensure_creator(db, workspace_id)
    rows = performance_rows(db, workspace_id)
    candidates = build_pattern_candidates(rows)
    changed: list[CreatorLearning] = []
    for candidate in candidates:
        existing = db.scalar(select(CreatorLearning).where(
            CreatorLearning.workspace_id == workspace_id,
            CreatorLearning.pattern_key == candidate["pattern_key"],
        ))
        old_status = existing.status if existing else ""
        old_direction = existing.direction if existing else ""
        status = next_learning_status(existing, candidate)
        values = {key: value for key, value in candidate.items() if key not in {"rows", "baseline"}}
        values.update({
            "workspace_id": workspace_id,
            "creator_profile_id": creator.id,
            "status": status,
            "raw": {
                "deterministic": True,
                "confidenceFormula": "sample 40% + consistency 25% + recency 20% + effect 15%",
                "platformContext": candidate["supporting_metrics"].get("platformContext"),
            },
        })
        if existing is None:
            learning_hash = stable_hash({"workspaceId": workspace_id, "patternKey": candidate["pattern_key"]})
            item = CreatorLearning(id=f"learning_{learning_hash[:28]}", **values)
            db.add(item)
            db.flush()
            action = "learning_generated"
        else:
            for key, value in values.items():
                setattr(existing, key, value)
            item = existing
            action = "learning_weakened" if status == "weakened" and old_status != "weakened" else "learning_validated"
        upsert_learning_evidence(db, item, candidate)
        db.flush()
        sync_learning_knowledge(db, item)
        log_activity(
            db,
            action,
            "CreatorLearning",
            item.id,
            {"sampleSize": item.sample_size, "confidence": item.confidence, "oldStatus": old_status, "oldDirection": old_direction, "status": status},
            workspace_id=workspace_id,
        )
        changed.append(item)

    db.flush()
    generate_strategy_suggestions(db, creator, changed)
    db.commit()
    learnings = list(db.scalars(select(CreatorLearning).where(CreatorLearning.workspace_id == workspace_id).options(selectinload(CreatorLearning.evidence)).order_by(CreatorLearning.confidence.desc())).all())
    suggestions = list(db.scalars(select(StrategySuggestion).where(StrategySuggestion.workspace_id == workspace_id).order_by(StrategySuggestion.updated_at.desc())).all())
    summary = creator_intelligence_summary(creator, learnings, rows)
    return learnings, suggestions, summary


def creator_intelligence_summary(creator: CreatorProfile, learnings: list[CreatorLearning], rows: list[dict[str, Any]]) -> dict[str, Any]:
    active = [item for item in learnings if item.status == "active"]
    hypotheses = [item for item in learnings if item.status in {"proposed", "weakened"}]
    recent = sorted(rows, key=lambda row: row["observed_at"], reverse=True)[:5]
    proven_contexts = {item.context_key for item in active}
    unexplored = [pillar for pillar in (creator.content_pillars or []) if pillar not in proven_contexts]
    return {
        "publishedSamples": len(rows),
        "activeLearningCount": len(active),
        "hypothesisCount": len(hypotheses),
        "provenPatterns": [item.learning_statement for item in active[:5]],
        "hypothesesToTest": [item.learning_statement for item in hypotheses[:5]],
        "unexploredOpportunities": unexplored[:5],
        "recentPerformance": [{"contentId": row["content"].id, "platform": row["platform"], "metrics": row["metrics"], "observedAt": row["observed_at"].isoformat()} for row in recent],
    }


def list_learnings(db: Session, workspace_id: str, status: str = "") -> list[CreatorLearning]:
    statement = select(CreatorLearning).where(CreatorLearning.workspace_id == workspace_id).options(selectinload(CreatorLearning.evidence))
    if status:
        statement = statement.where(CreatorLearning.status == status)
    return list(db.scalars(statement.order_by(CreatorLearning.confidence.desc(), CreatorLearning.updated_at.desc())).all())


def archive_learning(db: Session, learning_id: str, workspace_id: str) -> CreatorLearning:
    item = db.get(CreatorLearning, learning_id)
    ensure_owned(item, workspace_id, "CreatorLearning")
    if item.status != "archived":
        item.status = "archived"
        item.last_validated_at = utcnow()
        db.flush()
        sync_learning_knowledge(db, item)
        log_activity(db, "learning_archived", "CreatorLearning", item.id, {}, workspace_id=workspace_id)
        db.commit()
        db.refresh(item)
    return item


def decide_strategy_suggestion(db: Session, suggestion_id: str, workspace_id: str, decision: str) -> tuple[StrategySuggestion, CreatorProfile]:
    if decision not in STRATEGY_STATUSES - {"pending"}:
        raise WorkflowConflict("Unsupported Strategy Suggestion decision")
    item = db.scalar(select(StrategySuggestion).where(StrategySuggestion.id == suggestion_id).with_for_update())
    ensure_owned(item, workspace_id, "StrategySuggestion")
    creator = db.get(CreatorProfile, item.creator_profile_id)
    ensure_owned(creator, workspace_id, "CreatorProfile")
    if item.status != "pending":
        if item.status != decision:
            raise WorkflowConflict("Strategy Suggestion was already decided")
        return item, creator
    if decision == "accepted":
        change = item.proposed_change or {}
        model_field = STRATEGY_LIST_FIELDS.get(change.get("field"))
        if not model_field or change.get("action") != "add" or not str(change.get("value") or "").strip():
            raise WorkflowConflict("Strategy Suggestion change is not allowed")
        current = list(getattr(creator, model_field) or [])
        value = str(change["value"]).strip()
        if value not in current:
            current.append(value)
            setattr(creator, model_field, current)
        action = "strategy_suggestion_accepted"
    else:
        action = "strategy_suggestion_rejected" if decision == "rejected" else "strategy_suggestion_ignored"
    item.status = decision
    item.decided_at = utcnow()
    log_activity(db, action, "StrategySuggestion", item.id, {"proposedChange": item.proposed_change}, workspace_id=workspace_id)
    if decision == "accepted":
        log_activity(db, "creator_memory_updated", "CreatorProfile", creator.id, {"source": "StrategySuggestion", "suggestionId": item.id}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    db.refresh(creator)
    return item, creator


def active_learning_influence(db: Session, workspace_id: str, topic: Topic, candidate: dict[str, Any]) -> dict[str, Any]:
    learnings = list(db.scalars(select(CreatorLearning).where(
        CreatorLearning.workspace_id == workspace_id,
        CreatorLearning.status == "active",
    )).all())
    platforms = {str(value).casefold() for value in candidate.get("platform_fit") or []}
    recommended_format = str(candidate.get("recommended_format") or "").casefold()
    topic_text = f"{topic.category} {topic.title} {' '.join((topic.raw or {}).get('tags') or [])}".casefold()
    angle_text = str(candidate.get("content_opportunity") or "").casefold()
    relevant: list[CreatorLearning] = []
    explanations: list[str] = []
    adjustment = 0.0
    for learning in learnings:
        context = learning.context_key.casefold()
        match = (
            (learning.learning_type == "platform" and context in platforms)
            or (learning.learning_type == "format" and context in recommended_format)
            or (learning.learning_type == "topic_pillar" and context in topic_text)
            or (learning.learning_type in {"hook", "angle"} and context in angle_text)
        )
        if not match:
            continue
        relevant.append(learning)
        sign = 1 if learning.direction == "positive" else -1 if learning.direction == "negative" else 0
        points = sign * min(3.0, learning.confidence / 30.0)
        adjustment += points
        explanations.append(
            f"{learning.learning_statement} Confidence {learning.confidence} / n={learning.sample_size}，影响 {points:+.1f}。"
        )
    adjustment_int = max(-8, min(8, int(round(adjustment))))
    max_sample = max((item.sample_size for item in relevant), default=0)
    exploration_bonus = 4 if not relevant else 3 if max_sample < 3 else 1
    if not relevant:
        explanations.append("暂无直接匹配的 Active Learning，保留 exploration bonus，避免只推荐既有成功类型。")
    else:
        explanations.append(f"为防止反馈回路，Learning 调整封顶 ±8；本次 exploration bonus +{exploration_bonus}。")
    return {
        "learnings": relevant,
        "learning_adjustment": adjustment_int,
        "learning_explanation": explanations,
        "exploration_bonus": exploration_bonus,
    }


def _import_summary() -> dict[str, int]:
    return {"added": 0, "updated": 0, "skipped": 0, "failed": 0}


def import_creator_learning_records(db: Session, records: list[dict[str, Any]], workspace_id: str = DEFAULT_WORKSPACE_ID) -> dict[str, int]:
    """Import local fallback learnings only when their Analytics evidence is still traceable."""
    summary = _import_summary()
    creator = ensure_creator(db, workspace_id)
    for source in records:
        try:
            record_id = str(source.get("id") or "").strip()
            pattern_key = str(source.get("patternKey") or source.get("pattern_key") or "").strip()
            evidence_source = source.get("evidence") if isinstance(source.get("evidence"), list) else []
            valid_evidence: list[tuple[dict[str, Any], AnalyticsRecord]] = []
            for raw_evidence in evidence_source:
                analytics_id = raw_evidence.get("analyticsRecordId") or raw_evidence.get("analytics_record_id")
                analytics = db.get(AnalyticsRecord, analytics_id) if analytics_id else None
                if analytics is not None and analytics.workspace_id == workspace_id:
                    valid_evidence.append((raw_evidence, analytics))
            if not record_id or not pattern_key or not str(source.get("learningStatement") or source.get("learning_statement") or "").strip() or not valid_evidence:
                summary["failed"] += 1
                continue
            item = db.get(CreatorLearning, record_id) or db.scalar(select(CreatorLearning).where(
                CreatorLearning.workspace_id == workspace_id,
                CreatorLearning.pattern_key == pattern_key,
            ))
            created = item is None
            before = None if item is None else (
                item.learning_statement, item.status, item.sample_size, item.confidence,
                item.consistency, item.recency_score, item.effect_strength, item.supporting_metrics, item.raw,
            )
            status = str(source.get("status") or "proposed").casefold()
            if status not in LEARNING_STATUSES:
                status = "proposed"
            if item is not None and item.status == "archived":
                status = "archived"
            values = {
                "workspace_id": workspace_id,
                "creator_profile_id": creator.id,
                "pattern_key": pattern_key,
                "learning_statement": str(source.get("learningStatement") or source.get("learning_statement") or ""),
                "learning_type": str(source.get("learningType") or source.get("learning_type") or "pattern"),
                "context_key": str(source.get("contextKey") or source.get("context_key") or ""),
                "direction": str(source.get("direction") or "neutral"),
                "supporting_metrics": source.get("supportingMetrics") or source.get("supporting_metrics") or {},
                "sample_size": max(0, int(source.get("sampleSize") or source.get("sample_size") or len(valid_evidence))),
                "confidence": clamp(source.get("confidence")),
                "consistency": clamp(source.get("consistency")),
                "recency_score": clamp(source.get("recencyScore") or source.get("recency_score")),
                "effect_strength": clamp(source.get("effectStrength") or source.get("effect_strength")),
                "status": status,
                "last_validated_at": parse_datetime(source.get("lastValidatedAt") or source.get("last_validated_at")),
                "raw": {**(source.get("raw") or {}), "importedFromLocalStorage": True},
            }
            if item is None:
                item = CreatorLearning(id=record_id, **values)
                db.add(item)
            else:
                ensure_owned(item, workspace_id, "CreatorLearning")
                for key, value in values.items():
                    setattr(item, key, value)
            db.flush()
            for raw_evidence, analytics in valid_evidence:
                evidence = db.scalar(select(CreatorLearningEvidence).where(
                    CreatorLearningEvidence.learning_id == item.id,
                    CreatorLearningEvidence.analytics_record_id == analytics.id,
                ))
                content_id = raw_evidence.get("contentId") or raw_evidence.get("content_id") or analytics.content_id
                publishing_id = raw_evidence.get("publishJobId") or raw_evidence.get("publishing_task_id") or analytics.publishing_task_id
                opportunity_id = raw_evidence.get("opportunityId") or raw_evidence.get("opportunity_id")
                experience_id = raw_evidence.get("experienceRecordId") or raw_evidence.get("experience_record_id")
                if content_id and not db.get(Content, content_id):
                    content_id = None
                if publishing_id and not db.get(PublishingTask, publishing_id):
                    publishing_id = None
                if opportunity_id and not db.get(ContentOpportunity, opportunity_id):
                    opportunity_id = None
                if experience_id and not db.get(ExperienceRecord, experience_id):
                    experience_id = None
                evidence_values = {
                    "workspace_id": workspace_id,
                    "learning_id": item.id,
                    "content_id": content_id,
                    "opportunity_id": opportunity_id,
                    "publishing_task_id": publishing_id,
                    "analytics_record_id": analytics.id,
                    "experience_record_id": experience_id,
                    "tracking_snapshot_ids": raw_evidence.get("trackingSnapshotIds") or raw_evidence.get("tracking_snapshot_ids") or [],
                    "metrics": raw_evidence.get("metrics") or {},
                    "observed_at": parse_datetime(raw_evidence.get("observedAt") or raw_evidence.get("observed_at"), analytics.updated_at),
                    "supports": raw_evidence.get("supports") is not False,
                    "outcome_score": clamp(raw_evidence.get("outcomeScore") or raw_evidence.get("outcome_score"), -100, 100),
                    "raw": {**(raw_evidence.get("raw") or {}), "importedFromLocalStorage": True},
                }
                if evidence is None:
                    evidence = CreatorLearningEvidence(
                        id=str(raw_evidence.get("id") or f"evidence_{stable_hash(f'{item.id}|{analytics.id}')[:28]}"),
                        **evidence_values,
                    )
                    db.add(evidence)
                else:
                    for key, value in evidence_values.items():
                        setattr(evidence, key, value)
            db.flush()
            sync_learning_knowledge(db, item)
            after = (
                item.learning_statement, item.status, item.sample_size, item.confidence,
                item.consistency, item.recency_score, item.effect_strength, item.supporting_metrics, item.raw,
            )
            summary["added" if created else "updated" if before != after else "skipped"] += 1
        except Exception:
            summary["failed"] += 1
    return summary


def import_strategy_suggestion_records(db: Session, records: list[dict[str, Any]], workspace_id: str = DEFAULT_WORKSPACE_ID) -> dict[str, int]:
    summary = _import_summary()
    creator = ensure_creator(db, workspace_id)
    for source in records:
        try:
            record_id = str(source.get("id") or "").strip()
            change = source.get("proposedChange") or source.get("proposed_change") or {}
            fingerprint = str(source.get("fingerprint") or stable_hash({"workspace": workspace_id, "change": change}))
            if not record_id or not isinstance(change, dict):
                summary["failed"] += 1
                continue
            item = db.get(StrategySuggestion, record_id) or db.scalar(select(StrategySuggestion).where(
                StrategySuggestion.workspace_id == workspace_id,
                StrategySuggestion.fingerprint == fingerprint,
            ))
            created = item is None
            before = None if item is None else (item.statement, item.rationale, item.status, item.proposed_change, item.raw)
            status = str(source.get("status") or "pending").casefold()
            if status not in STRATEGY_STATUSES:
                status = "pending"
            if item is not None and item.status != "pending":
                status = item.status
            learning_ids = [learning_id for learning_id in (source.get("supportingLearningIds") or source.get("supporting_learning_ids") or []) if db.get(CreatorLearning, learning_id)]
            values = {
                "workspace_id": workspace_id,
                "creator_profile_id": creator.id,
                "fingerprint": fingerprint,
                "suggestion_type": str(source.get("suggestionType") or source.get("suggestion_type") or change.get("field") or "strategy"),
                "statement": str(source.get("statement") or "Strategy Suggestion"),
                "proposed_change": change,
                "rationale": str(source.get("rationale") or ""),
                "supporting_learning_ids": learning_ids,
                "status": status,
                "decided_at": (
                    parse_datetime(source.get("decidedAt") or source.get("decided_at"))
                    if source.get("decidedAt") or source.get("decided_at")
                    else item.decided_at if item is not None and status != "pending"
                    else None
                ),
                "raw": {**(source.get("raw") or {}), "importedFromLocalStorage": True, "humanApprovalRequired": True},
            }
            if item is None:
                item = StrategySuggestion(id=record_id, **values)
                db.add(item)
            else:
                ensure_owned(item, workspace_id, "StrategySuggestion")
                for key, value in values.items():
                    setattr(item, key, value)
            db.flush()
            after = (item.statement, item.rationale, item.status, item.proposed_change, item.raw)
            summary["added" if created else "updated" if before != after else "skipped"] += 1
        except Exception:
            summary["failed"] += 1
    return summary
