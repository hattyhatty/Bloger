"""Minimal Generated Asset API; this is not a media-library surface."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import get_db
from .generated_assets import asset_file, get_asset_for_result
from .models import GeneratedAsset
from .queue import enqueue_asset_persistence
from .schemas import GeneratedAssetOut
from .storage import get_storage_adapter
from .workflow import ensure_owned


router = APIRouter(tags=["generated-assets"])


@router.get("/api/generated-assets/{asset_id}", response_model=GeneratedAssetOut)
def generated_asset(asset_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    item = db.get(GeneratedAsset, asset_id)
    ensure_owned(item, workspace_id, "GeneratedAsset")
    return item


@router.get("/api/video-results/{result_id}/asset", response_model=GeneratedAssetOut)
def result_asset(result_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    item = get_asset_for_result(db, result_id, workspace_id)
    if not item:
        raise HTTPException(status_code=404, detail="Generated Asset not found")
    return item


@router.post("/api/video-results/{result_id}/asset/retry", response_model=GeneratedAssetOut)
def retry_result_asset(result_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    enqueue_asset_persistence(db, result_id, workspace_id)
    item = get_asset_for_result(db, result_id, workspace_id)
    return item


@router.get("/api/generated-assets/{asset_id}/content")
def generated_asset_content(asset_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    item, path = asset_file(db, asset_id, workspace_id, get_storage_adapter())
    return FileResponse(path, media_type=item.mime_type or "video/mp4", filename=f"{item.id}.mp4")
