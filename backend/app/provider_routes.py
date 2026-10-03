"""Backend-only video provider configuration status and safe diagnostics."""
from dataclasses import asdict

from fastapi import APIRouter

from .config import get_settings
from .providers import FakeVideoProvider, ProviderError
from .runway_provider import RUNWAY_CAPABILITIES, RunwayVideoProvider

router = APIRouter(prefix="/api/video-providers", tags=["video-providers"])


@router.get("")
def provider_status():
    settings = get_settings()
    return {
        "providers": [
            {"id": "Fake", "configured": True, "default_model": "fake-v1",
             "capabilities": asdict(FakeVideoProvider.capabilities)},
            {"id": "Runway", "configured": bool(settings.runwayml_api_secret.strip()),
             "default_model": settings.runway_default_model,
             "capabilities": asdict(RUNWAY_CAPABILITIES)},
        ]
    }


@router.post("/runway/test")
def test_runway_connection():
    provider = RunwayVideoProvider()
    if not provider.configured:
        return {"ok": False, "configured": False, "message": "RUNWAYML_API_SECRET is not configured"}
    try:
        return {**provider.test_connection(), "configured": True}
    except ProviderError as exc:
        return {"ok": False, "configured": True, "message": str(exc)}
