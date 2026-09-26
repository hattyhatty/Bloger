"""Structured, human-reviewed AI video production planning services."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .activity import log_activity
from .intelligence import ensure_creator
from .models import (
    Content,
    ContentOpportunity,
    CreatorLearning,
    KnowledgeEntry,
    VideoGenerationPrompt,
    VideoProductionPlan,
    VideoScript,
    VideoShot,
    VideoStoryboard,
)
from .workflow import DEFAULT_WORKSPACE_ID, WorkflowConflict, ensure_owned, stable_hash


PLAN_STATUSES = {"draft", "planned", "in_production", "ready_for_review"}
PROMPT_TARGETS = {"Generic", "Seedance", "Kling", "Veo", "Runway"}


def content_snapshot(content: Content) -> dict[str, Any]:
    raw = content.raw or {}
    return {
        "id": content.id,
        "revision": content.revision,
        "contentHash": content.content_hash,
        "title": content.title,
        "platform": content.platform,
        "contentType": content.content_type,
        "sourceUrl": content.source_url,
        "draftTitle": raw.get("draftTitle") or content.title,
        "draftHook": raw.get("draftHook") or raw.get("recommendedHook") or "",
        "draftBody": raw.get("draftBody") or raw.get("body") or "",
        "draftTags": raw.get("draftTags") or raw.get("tags") or [],
        "selectedAngle": raw.get("selectedAngle") or raw.get("recommendedAngle") or "",
        "sourceTopicId": content.topic_id,
        "sourceOpportunityId": raw.get("sourceOpportunityId") or "",
        "relevantKnowledgeIds": raw.get("relevantKnowledgeIds") or [],
        "relevantLearningIds": raw.get("relevantLearningIds") or [],
    }


def validate_plan_status(db: Session, plan: VideoProductionPlan, status: str) -> None:
    if status == "draft":
        return
    script = db.scalar(select(VideoScript).where(VideoScript.plan_id == plan.id))
    if script is None:
        raise WorkflowConflict("Generate and review the Script before advancing the Video Plan")
    if status == "planned":
        return
    storyboard = db.scalar(select(VideoStoryboard).where(VideoStoryboard.plan_id == plan.id))
    if storyboard is None:
        raise WorkflowConflict("Generate and review the Storyboard before production")
    shots = list(db.scalars(select(VideoShot).where(VideoShot.storyboard_id == storyboard.id)).all())
    if not shots:
        raise WorkflowConflict("Storyboard must contain at least one Shot")
    if status == "in_production":
        return
    prompt_shot_ids = set(db.scalars(select(VideoGenerationPrompt.shot_id).where(
        VideoGenerationPrompt.shot_id.in_([shot.id for shot in shots]),
    )).all())
    if any(shot.id not in prompt_shot_ids for shot in shots):
        raise WorkflowConflict("Every Shot needs at least one Generation Prompt before review")


def create_video_plan(db: Session, values: dict[str, Any]) -> VideoProductionPlan:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    content = db.get(Content, values.get("content_id"))
    ensure_owned(content, workspace_id, "Content")
    existing = db.scalar(select(VideoProductionPlan).where(
        VideoProductionPlan.workspace_id == workspace_id,
        VideoProductionPlan.content_id == content.id,
        VideoProductionPlan.content_revision == content.revision,
    ))
    if existing:
        return existing
    raw = content.raw or {}
    opportunity_id = raw.get("sourceOpportunityId") or None
    if opportunity_id:
        opportunity = db.get(ContentOpportunity, opportunity_id)
        ensure_owned(opportunity, workspace_id, "ContentOpportunity")
        if opportunity.developed_content_id and opportunity.developed_content_id != content.id:
            raise WorkflowConflict("Opportunity was developed into another Content")
    plan_id = values.get("id") or f"video_plan_{stable_hash({'contentId': content.id, 'revision': content.revision})[:28]}"
    if db.get(VideoProductionPlan, plan_id):
        raise WorkflowConflict("Video Plan id already belongs to another record")
    plan = VideoProductionPlan(
        id=plan_id,
        workspace_id=workspace_id,
        content_id=content.id,
        opportunity_id=opportunity_id,
        content_revision=content.revision,
        content_hash=content.content_hash,
        content_snapshot=content_snapshot(content),
        video_concept=values.get("video_concept") or raw.get("selectedAngle") or raw.get("recommendedAngle") or content.title,
        target_platform=values.get("target_platform") or content.platform or "抖音",
        target_duration_seconds=int(values.get("target_duration_seconds") or 60),
        content_format=values.get("content_format") or content.content_type or "口播",
        visual_style=values.get("visual_style") or "清晰、现代、具有信息层次",
        aspect_ratio=values.get("aspect_ratio") or "9:16",
        status="draft",
        raw=values.get("raw") or {},
    )
    db.add(plan)
    log_activity(db, "video_plan_created", "VideoProductionPlan", plan.id, {
        "contentId": content.id,
        "contentRevision": content.revision,
        "contentHash": content.content_hash,
    }, workspace_id=workspace_id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        concurrent = db.scalar(select(VideoProductionPlan).where(
            VideoProductionPlan.workspace_id == workspace_id,
            VideoProductionPlan.content_id == content.id,
            VideoProductionPlan.content_revision == content.revision,
        ))
        if concurrent:
            return concurrent
        raise
    db.refresh(plan)
    return plan


def update_video_plan(db: Session, plan_id: str, values: dict[str, Any]) -> VideoProductionPlan:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    plan = db.scalar(select(VideoProductionPlan).where(VideoProductionPlan.id == plan_id).with_for_update())
    ensure_owned(plan, workspace_id, "VideoProductionPlan")
    old_status = plan.status
    new_status = values.get("status") or old_status
    if new_status not in PLAN_STATUSES:
        raise WorkflowConflict("Unsupported Video Plan status")
    validate_plan_status(db, plan, new_status)
    for field in ("video_concept", "target_platform", "target_duration_seconds", "content_format", "visual_style", "aspect_ratio", "raw"):
        if field in values:
            setattr(plan, field, values[field])
    plan.status = new_status
    log_activity(db, "video_plan_status_changed" if new_status != old_status else "video_plan_updated", "VideoProductionPlan", plan.id, {
        "oldStatus": old_status,
        "status": new_status,
        "boundContentRevision": plan.content_revision,
    }, workspace_id=workspace_id)
    db.commit()
    db.refresh(plan)
    return plan


def set_video_plan_status(db: Session, plan_id: str, workspace_id: str, status: str) -> VideoProductionPlan:
    if status not in PLAN_STATUSES:
        raise WorkflowConflict("Unsupported Video Plan status")
    plan = db.scalar(select(VideoProductionPlan).where(VideoProductionPlan.id == plan_id).with_for_update())
    ensure_owned(plan, workspace_id, "VideoProductionPlan")
    validate_plan_status(db, plan, status)
    if plan.status != status:
        old_status = plan.status
        plan.status = status
        log_activity(db, "video_plan_status_changed", "VideoProductionPlan", plan.id, {"oldStatus": old_status, "status": status}, workspace_id=workspace_id)
        db.commit()
        db.refresh(plan)
    return plan


def video_plan_context(db: Session, plan_id: str, workspace_id: str) -> dict[str, Any]:
    plan = db.get(VideoProductionPlan, plan_id)
    ensure_owned(plan, workspace_id, "VideoProductionPlan")
    content = db.get(Content, plan.content_id)
    ensure_owned(content, workspace_id, "Content")
    creator = ensure_creator(db, workspace_id)
    raw = content.raw or {}
    knowledge_ids = list(dict.fromkeys(raw.get("relevantKnowledgeIds") or []))
    learning_ids = list(dict.fromkeys(raw.get("relevantLearningIds") or []))
    knowledge = list(db.scalars(select(KnowledgeEntry).where(
        KnowledgeEntry.workspace_id == workspace_id,
        KnowledgeEntry.status == "ACTIVE",
        KnowledgeEntry.id.in_(knowledge_ids),
    )).all()) if knowledge_ids else []
    learnings = list(db.scalars(select(CreatorLearning).where(
        CreatorLearning.workspace_id == workspace_id,
        CreatorLearning.status == "active",
        CreatorLearning.id.in_(learning_ids),
    )).all()) if learning_ids else []
    opportunity = db.get(ContentOpportunity, plan.opportunity_id) if plan.opportunity_id else None
    if opportunity:
        ensure_owned(opportunity, workspace_id, "ContentOpportunity")
    return {"content": content, "opportunity": opportunity, "creator_memory": creator, "knowledge": knowledge, "learnings": learnings}


def _source_context(db: Session, plan: VideoProductionPlan) -> dict[str, Any]:
    context = video_plan_context(db, plan.id, plan.workspace_id)
    return {
        "contentId": plan.content_id,
        "contentRevision": plan.content_revision,
        "contentHash": plan.content_hash,
        "opportunityId": plan.opportunity_id or "",
        "creatorProfileId": context["creator_memory"].id,
        "knowledgeIds": [item.id for item in context["knowledge"]],
        "learningIds": [item.id for item in context["learnings"]],
    }


def save_video_script(db: Session, plan_id: str, values: dict[str, Any]) -> VideoScript:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    plan = db.get(VideoProductionPlan, plan_id)
    ensure_owned(plan, workspace_id, "VideoProductionPlan")
    item = db.scalar(select(VideoScript).where(VideoScript.plan_id == plan.id).with_for_update())
    created = item is None
    script_id = values.get("id") or f"video_script_{stable_hash(plan.id)[:28]}"
    fields = {key: values.get(key) for key in ("hook", "narration_dialogue", "main_story_flow", "ending_cta", "estimated_duration_seconds", "raw")}
    fields["source_context"] = _source_context(db, plan)
    if item is None:
        item = VideoScript(id=script_id, workspace_id=workspace_id, plan_id=plan.id, revision=1, **fields)
        db.add(item)
    else:
        if values.get("id") and values["id"] != item.id:
            raise WorkflowConflict("Video Plan already has a Script")
        changed = any(getattr(item, key) != value for key, value in fields.items())
        for key, value in fields.items():
            setattr(item, key, value)
        if changed:
            item.revision += 1
    operation = values.get("operation") or "manual"
    action = "video_script_generated" if operation == "generated" else "video_script_updated"
    log_activity(db, action, "VideoScript", item.id, {"planId": plan.id, "created": created, "revision": item.revision}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    return item


def save_storyboard(db: Session, plan_id: str, values: dict[str, Any], generated_shots: list[dict[str, Any]] | None = None) -> VideoStoryboard:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    plan = db.get(VideoProductionPlan, plan_id)
    ensure_owned(plan, workspace_id, "VideoProductionPlan")
    script = db.scalar(select(VideoScript).where(VideoScript.plan_id == plan.id))
    if script is None:
        raise WorkflowConflict("Create and review the Script before Storyboard generation")
    item = db.scalar(select(VideoStoryboard).where(VideoStoryboard.plan_id == plan.id).with_for_update())
    if generated_shots is not None and item is not None and item.shots:
        raise WorkflowConflict("Storyboard already has Shots; edit or remove them before generating again")
    created = item is None
    fields = {key: values.get(key) or "" for key in (
        "recurring_character_description", "clothing", "environment", "visual_style", "reference_notes"
    )}
    fields["raw"] = values.get("raw") or {}
    if item is None:
        item = VideoStoryboard(
            id=values.get("id") or f"video_storyboard_{stable_hash(plan.id)[:28]}",
            workspace_id=workspace_id,
            plan_id=plan.id,
            script_id=script.id,
            revision=1,
            **fields,
        )
        db.add(item)
        db.flush()
    else:
        changed = any(getattr(item, key) != value for key, value in fields.items()) or item.script_id != script.id
        for key, value in fields.items():
            setattr(item, key, value)
        item.script_id = script.id
        if changed:
            item.revision += 1
    if generated_shots is not None:
        for index, shot_values in enumerate(generated_shots, start=1):
            db.add(VideoShot(
                id=shot_values.get("id") or f"video_shot_{stable_hash({'storyboard': item.id, 'number': index})[:28]}",
                workspace_id=workspace_id,
                storyboard_id=item.id,
                shot_number=index,
                estimated_duration_seconds=int(shot_values.get("estimated_duration_seconds") or 5),
                scene_description=shot_values.get("scene_description") or "",
                subject_character=shot_values.get("subject_character") or fields["recurring_character_description"],
                action=shot_values.get("action") or "",
                environment=shot_values.get("environment") or fields["environment"],
                camera_framing=shot_values.get("camera_framing") or "",
                camera_movement=shot_values.get("camera_movement") or "",
                lighting_mood=shot_values.get("lighting_mood") or "",
                narration_dialogue=shot_values.get("narration_dialogue") or "",
                transition=shot_values.get("transition") or "",
                generation_notes=shot_values.get("generation_notes") or "",
                raw=shot_values.get("raw") or {},
            ))
    operation = values.get("operation") or "manual"
    action = "video_storyboard_generated" if operation == "generated" else "video_storyboard_updated"
    log_activity(db, action, "VideoStoryboard", item.id, {"planId": plan.id, "created": created, "shotCount": len(generated_shots or [])}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    return item


def add_shot(db: Session, storyboard_id: str, values: dict[str, Any]) -> VideoShot:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    storyboard = db.get(VideoStoryboard, storyboard_id)
    ensure_owned(storyboard, workspace_id, "VideoStoryboard")
    shots = list(db.scalars(select(VideoShot).where(VideoShot.storyboard_id == storyboard.id).order_by(VideoShot.shot_number)).all())
    number = int(values.get("shot_number") or len(shots) + 1)
    if number != len(shots) + 1:
        raise WorkflowConflict("Add a Shot at the end, then use reorder")
    item = VideoShot(
        id=values.get("id") or f"video_shot_{stable_hash({'storyboard': storyboard.id, 'nonce': len(shots) + 1, 'count': len(shots)})[:28]}",
        workspace_id=workspace_id,
        storyboard_id=storyboard.id,
        shot_number=number,
        **{key: values.get(key) or (5 if key == "estimated_duration_seconds" else {} if key == "raw" else "") for key in (
            "estimated_duration_seconds", "scene_description", "subject_character", "action", "environment",
            "camera_framing", "camera_movement", "lighting_mood", "narration_dialogue", "transition", "generation_notes", "raw"
        )},
    )
    db.add(item)
    log_activity(db, "video_shot_added", "VideoShot", item.id, {"storyboardId": storyboard.id, "shotNumber": number}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    return item


def update_shot(db: Session, shot_id: str, values: dict[str, Any]) -> VideoShot:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    item = db.scalar(select(VideoShot).where(VideoShot.id == shot_id).with_for_update())
    ensure_owned(item, workspace_id, "VideoShot")
    requested_number = values.get("shot_number")
    if requested_number and int(requested_number) != item.shot_number:
        raise WorkflowConflict("Use the reorder endpoint to change Shot order")
    for key in (
        "estimated_duration_seconds", "scene_description", "subject_character", "action", "environment",
        "camera_framing", "camera_movement", "lighting_mood", "narration_dialogue", "transition", "generation_notes", "raw"
    ):
        if key in values:
            setattr(item, key, values[key])
    log_activity(db, "video_shot_updated", "VideoShot", item.id, {"storyboardId": item.storyboard_id, "shotNumber": item.shot_number}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    return item


def remove_shot(db: Session, shot_id: str, workspace_id: str) -> None:
    item = db.scalar(select(VideoShot).where(VideoShot.id == shot_id).with_for_update())
    ensure_owned(item, workspace_id, "VideoShot")
    storyboard_id = item.storyboard_id
    removed_number = item.shot_number
    db.delete(item)
    db.flush()
    remaining = list(db.scalars(select(VideoShot).where(VideoShot.storyboard_id == storyboard_id).order_by(VideoShot.shot_number)).all())
    temporary_offset = 1000 + len(remaining)
    for shot in remaining:
        shot.shot_number = temporary_offset + shot.shot_number
    db.flush()
    for index, shot in enumerate(remaining, start=1):
        shot.shot_number = index
    log_activity(db, "video_shot_removed", "VideoShot", shot_id, {"storyboardId": storyboard_id, "shotNumber": removed_number}, workspace_id=workspace_id)
    db.commit()


def reorder_shots(db: Session, storyboard_id: str, workspace_id: str, shot_ids: list[str]) -> list[VideoShot]:
    storyboard = db.scalar(select(VideoStoryboard).where(VideoStoryboard.id == storyboard_id).with_for_update())
    ensure_owned(storyboard, workspace_id, "VideoStoryboard")
    shots = list(db.scalars(select(VideoShot).where(VideoShot.storyboard_id == storyboard.id)).all())
    if len(shot_ids) != len(shots) or set(shot_ids) != {shot.id for shot in shots}:
        raise WorkflowConflict("Shot reorder must include every Shot exactly once")
    lookup = {shot.id: shot for shot in shots}
    temporary_offset = 1000 + len(shots)
    for shot in shots:
        shot.shot_number = temporary_offset + shot.shot_number
    db.flush()
    for index, shot_id in enumerate(shot_ids, start=1):
        lookup[shot_id].shot_number = index
    log_activity(db, "video_shots_reordered", "VideoStoryboard", storyboard.id, {"shotIds": shot_ids}, workspace_id=workspace_id)
    db.commit()
    return list(db.scalars(select(VideoShot).where(VideoShot.storyboard_id == storyboard.id).order_by(VideoShot.shot_number)).all())


def shot_source_hash(shot: VideoShot) -> str:
    storyboard = shot.storyboard
    return stable_hash({
        "shot": {
            "number": shot.shot_number,
            "duration": shot.estimated_duration_seconds,
            "scene": shot.scene_description,
            "subject": shot.subject_character,
            "action": shot.action,
            "environment": shot.environment,
            "framing": shot.camera_framing,
            "movement": shot.camera_movement,
            "lighting": shot.lighting_mood,
            "narration": shot.narration_dialogue,
            "transition": shot.transition,
            "notes": shot.generation_notes,
        },
        "consistency": {
            "character": storyboard.recurring_character_description,
            "clothing": storyboard.clothing,
            "environment": storyboard.environment,
            "visualStyle": storyboard.visual_style,
            "referenceNotes": storyboard.reference_notes,
        },
    })


def save_shot_prompt(db: Session, shot_id: str, values: dict[str, Any]) -> VideoGenerationPrompt:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    shot = db.scalar(select(VideoShot).where(VideoShot.id == shot_id).options(selectinload(VideoShot.storyboard)).with_for_update())
    ensure_owned(shot, workspace_id, "VideoShot")
    target = values.get("prompt_target") or "Generic"
    if target not in PROMPT_TARGETS:
        raise WorkflowConflict("Unsupported Video Prompt target")
    item = db.scalar(select(VideoGenerationPrompt).where(
        VideoGenerationPrompt.shot_id == shot.id,
        VideoGenerationPrompt.prompt_target == target,
    ).with_for_update())
    existed = item is not None
    fields = {key: values.get(key) or "" for key in (
        "generic_video_prompt", "image_reference_prompt", "negative_instructions", "continuity_notes"
    )}
    fields["raw"] = values.get("raw") or {}
    source_hash = shot_source_hash(shot)
    if item is None:
        item = VideoGenerationPrompt(
            id=values.get("id") or f"video_prompt_{stable_hash({'shot': shot.id, 'target': target})[:28]}",
            workspace_id=workspace_id,
            shot_id=shot.id,
            prompt_target=target,
            source_shot_hash=source_hash,
            revision=1,
            **fields,
        )
        db.add(item)
    else:
        changed = source_hash != item.source_shot_hash or any(getattr(item, key) != value for key, value in fields.items())
        for key, value in fields.items():
            setattr(item, key, value)
        item.source_shot_hash = source_hash
        if changed:
            item.revision += 1
    operation = values.get("operation") or "manual"
    action = "video_prompt_regenerated" if operation == "generated" and existed else "video_prompt_generated" if operation == "generated" else "video_prompt_updated"
    log_activity(db, action, "VideoGenerationPrompt", item.id, {"shotId": shot.id, "target": target, "revision": item.revision}, workspace_id=workspace_id)
    db.commit()
    db.refresh(item)
    return item


def get_plan_workspace(db: Session, plan_id: str, workspace_id: str) -> dict[str, Any]:
    plan = db.scalar(select(VideoProductionPlan).where(VideoProductionPlan.id == plan_id).options(
        selectinload(VideoProductionPlan.content),
        selectinload(VideoProductionPlan.script),
        selectinload(VideoProductionPlan.storyboard).selectinload(VideoStoryboard.shots).selectinload(VideoShot.prompts),
    ))
    ensure_owned(plan, workspace_id, "VideoProductionPlan")
    storyboard = plan.storyboard
    shots = list(storyboard.shots) if storyboard else []
    prompts = [prompt for shot in shots for prompt in shot.prompts]
    return {"plan": plan, "script": plan.script, "storyboard": storyboard, "shots": shots, "prompts": prompts}
