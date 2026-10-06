"""Generated-result persistence services, independent of video providers."""
from __future__ import annotations

from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.orm import Session

from .activity import log_activity
from .models import GeneratedAsset, VideoGenerationResult
from .storage import StorageAdapter, StorageError
from .workflow import WorkflowConflict, ensure_owned, stable_hash, utcnow


def _asset_id(result_id: str) -> str:
    return "generated_asset_" + stable_hash({"generationResultId": result_id})[:32]


def _storage_key(workspace_id: str, asset_id: str) -> str:
    workspace_key = stable_hash({"workspaceId": workspace_id})[:16]
    asset_key = stable_hash({"assetId": asset_id})[:32]
    return f"{workspace_key}/asset_{asset_key}.mp4"


def _durable_url(asset_id: str, workspace_id: str) -> str:
    return f"/api/generated-assets/{quote(asset_id, safe='')}/content?workspace_id={quote(workspace_id, safe='')}"


def create_or_get_asset(db: Session, result: VideoGenerationResult, *, commit: bool = False) -> GeneratedAsset:
    existing = db.scalar(select(GeneratedAsset).where(
        GeneratedAsset.generation_result_id == result.id
    ).with_for_update())
    if existing:
        ensure_owned(existing, result.workspace_id, "GeneratedAsset")
        return existing
    if not result.result_url:
        raise WorkflowConflict("Generated Result has no provider URL to persist")
    asset_id = _asset_id(result.id)
    item = GeneratedAsset(
        id=asset_id,
        workspace_id=result.workspace_id,
        generation_result_id=result.id,
        source_provider=result.provider,
        source_url=result.result_url,
        storage_provider="local",
        storage_key=_storage_key(result.workspace_id, asset_id),
        durable_url=_durable_url(asset_id, result.workspace_id),
        mime_type="",
        file_size=0,
        sha256="",
        status="pending",
        last_error="",
    )
    db.add(item)
    db.flush()
    log_activity(db, "generated_asset_created", "GeneratedAsset", item.id, {
        "generationResultId": result.id,
        "sourceProvider": result.provider,
        "storageProvider": item.storage_provider,
    }, workspace_id=result.workspace_id)
    if commit:
        db.commit()
        db.refresh(item)
    return item


def get_asset_for_result(db: Session, result_id: str, workspace_id: str) -> GeneratedAsset | None:
    result = db.get(VideoGenerationResult, result_id)
    ensure_owned(result, workspace_id, "VideoGenerationResult")
    item = db.scalar(select(GeneratedAsset).where(GeneratedAsset.generation_result_id == result.id))
    if item:
        ensure_owned(item, workspace_id, "GeneratedAsset")
    return item


def persist_asset(db: Session, asset_id: str, workspace_id: str, adapter: StorageAdapter) -> GeneratedAsset:
    asset = db.scalar(select(GeneratedAsset).where(GeneratedAsset.id == asset_id).with_for_update())
    ensure_owned(asset, workspace_id, "GeneratedAsset")
    result = db.get(VideoGenerationResult, asset.generation_result_id)
    ensure_owned(result, workspace_id, "VideoGenerationResult")
    if asset.status == "archived":
        raise WorkflowConflict("Archived Generated Asset cannot be persisted")
    if asset.status == "stored" and adapter.exists(asset.storage_key):
        return asset
    asset.status = "pending"
    asset.last_error = ""
    db.commit()

    stored = adapter.store_from_url(asset.source_url, asset.storage_key, metadata={
        "asset_id": asset.id,
        "generation_result_id": result.id,
        "source_provider": asset.source_provider,
    })

    asset = db.scalar(select(GeneratedAsset).where(GeneratedAsset.id == asset_id).with_for_update())
    ensure_owned(asset, workspace_id, "GeneratedAsset")
    asset.storage_provider = adapter.provider
    asset.mime_type = stored.mime_type
    asset.file_size = stored.file_size
    asset.sha256 = stored.sha256
    asset.status = "stored"
    asset.last_error = ""
    asset.stored_at = utcnow()
    log_activity(db, "generated_asset_stored", "GeneratedAsset", asset.id, {
        "generationResultId": asset.generation_result_id,
        "storageProvider": asset.storage_provider,
        "fileSize": asset.file_size,
        "sha256": asset.sha256,
        "mimeType": asset.mime_type,
    }, workspace_id=workspace_id)
    db.commit()
    db.refresh(asset)
    return asset


def mark_asset_failed(db: Session, asset_id: str, workspace_id: str, error: Exception | str) -> GeneratedAsset:
    asset = db.scalar(select(GeneratedAsset).where(GeneratedAsset.id == asset_id).with_for_update())
    ensure_owned(asset, workspace_id, "GeneratedAsset")
    if asset.status != "stored":
        asset.status = "failed"
        asset.last_error = str(error)[:1000]
        log_activity(db, "generated_asset_failed", "GeneratedAsset", asset.id, {
            "generationResultId": asset.generation_result_id,
            "error": asset.last_error,
        }, workspace_id=workspace_id)
        db.commit()
        db.refresh(asset)
    return asset


def asset_file(db: Session, asset_id: str, workspace_id: str, adapter: StorageAdapter):
    asset = db.get(GeneratedAsset, asset_id)
    ensure_owned(asset, workspace_id, "GeneratedAsset")
    if asset.status != "stored":
        raise WorkflowConflict("Generated Asset is not stored")
    path = adapter.path_for(asset.storage_key)
    if not path.is_file():
        raise WorkflowConflict("Generated Asset file is unavailable")
    return asset, path
