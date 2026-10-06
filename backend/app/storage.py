"""Provider-independent durable binary storage boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
from typing import Callable
from urllib.parse import urljoin, urlparse

import httpx

from .config import Settings, get_settings


class StorageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredObject:
    storage_key: str
    path: Path
    mime_type: str
    file_size: int
    sha256: str


class StorageAdapter:
    provider = "unknown"

    def store_from_url(self, source_url: str, storage_key: str, *, metadata: dict | None = None) -> StoredObject:
        raise NotImplementedError

    def exists(self, storage_key: str) -> bool:
        raise NotImplementedError

    def path_for(self, storage_key: str) -> Path:
        raise NotImplementedError


def _default_resolver(host: str) -> list[str]:
    return list(dict.fromkeys(item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)))


class LocalStorageAdapter(StorageAdapter):
    provider = "local"
    _KEY = re.compile(r"^[a-f0-9]{16}/asset_[a-f0-9]{32}\.mp4$")
    _MIME_TYPES = {"video/mp4", "application/mp4"}

    def __init__(self, settings: Settings | None = None, client: httpx.Client | None = None,
                 resolver: Callable[[str], list[str]] | None = None):
        self.settings = settings or get_settings()
        configured = Path(self.settings.generated_asset_storage_dir)
        backend_root = Path(__file__).resolve().parents[1]
        self.root = (configured if configured.is_absolute() else backend_root / configured).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.client = client or httpx.Client(timeout=self.settings.generated_asset_download_timeout_seconds)
        self.resolver = resolver or _default_resolver

    def path_for(self, storage_key: str) -> Path:
        if not self._KEY.fullmatch(storage_key or ""):
            raise StorageError("Invalid generated asset storage key")
        target = (self.root / storage_key).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise StorageError("Generated asset path escapes storage root") from exc
        return target

    def exists(self, storage_key: str) -> bool:
        try:
            return self.path_for(storage_key).is_file()
        except StorageError:
            return False

    def _validate_url(self, value: str) -> str:
        parsed = urlparse(str(value or "").strip())
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise StorageError("Generated asset source must be an HTTPS URL without credentials")
        try:
            addresses = self.resolver(parsed.hostname)
        except OSError as exc:
            raise StorageError("Generated asset source host could not be resolved") from exc
        if not addresses:
            raise StorageError("Generated asset source host has no address")
        for value in addresses:
            try:
                address = ipaddress.ip_address(value)
            except ValueError as exc:
                raise StorageError("Generated asset source resolved to an invalid address") from exc
            if not address.is_global:
                raise StorageError("Generated asset source must resolve to a public address")
        return parsed.geturl()

    @staticmethod
    def _digest(path: Path) -> tuple[int, str]:
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                size += len(chunk)
                digest.update(chunk)
        return size, digest.hexdigest()

    @staticmethod
    def _atomic_json(path: Path, values: dict):
        temporary = path.with_suffix(path.suffix + ".part")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(values, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def _finalize_existing(self, storage_key: str, target: Path, metadata: dict | None) -> StoredObject:
        size, digest = self._digest(target)
        if size > self.settings.generated_asset_max_bytes:
            raise StorageError("Stored generated asset exceeds configured size limit")
        values = {
            **(metadata or {}),
            "storage_provider": self.provider,
            "storage_key": storage_key,
            "mime_type": "video/mp4",
            "file_size": size,
            "sha256": digest,
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
        self._atomic_json(target.with_suffix(target.suffix + ".json"), values)
        return StoredObject(storage_key, target, "video/mp4", size, digest)

    def store_from_url(self, source_url: str, storage_key: str, *, metadata: dict | None = None) -> StoredObject:
        target = self.path_for(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file():
            return self._finalize_existing(storage_key, target, metadata)

        temporary = target.with_suffix(target.suffix + ".part")
        temporary.unlink(missing_ok=True)
        current = self._validate_url(source_url)
        try:
            for redirect_count in range(4):
                with self.client.stream("GET", current, headers={"Accept": "video/mp4"}, follow_redirects=False) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("Location")
                        if not location or redirect_count == 3:
                            raise StorageError("Generated asset download exceeded redirect limit")
                        current = self._validate_url(urljoin(current, location))
                        continue
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as exc:
                        raise StorageError(f"Generated asset download returned HTTP {response.status_code}") from exc
                    mime_type = (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
                    if mime_type not in self._MIME_TYPES:
                        raise StorageError(f"Generated asset Content-Type is not MP4: {mime_type or 'missing'}")
                    length = response.headers.get("Content-Length")
                    if length:
                        try:
                            if int(length) > self.settings.generated_asset_max_bytes:
                                raise StorageError("Generated asset exceeds configured size limit")
                        except ValueError as exc:
                            raise StorageError("Generated asset Content-Length is invalid") from exc
                    digest = hashlib.sha256()
                    size = 0
                    with temporary.open("wb") as stream:
                        for chunk in response.iter_bytes(1024 * 1024):
                            size += len(chunk)
                            if size > self.settings.generated_asset_max_bytes:
                                raise StorageError("Generated asset exceeds configured size limit")
                            digest.update(chunk)
                            stream.write(chunk)
                        stream.flush()
                        os.fsync(stream.fileno())
                    if size <= 0:
                        raise StorageError("Generated asset download was empty")
                    os.replace(temporary, target)
                    values = {
                        **(metadata or {}),
                        "storage_provider": self.provider,
                        "storage_key": storage_key,
                        "mime_type": mime_type,
                        "file_size": size,
                        "sha256": digest.hexdigest(),
                        "stored_at": datetime.now(timezone.utc).isoformat(),
                    }
                    self._atomic_json(target.with_suffix(target.suffix + ".json"), values)
                    return StoredObject(storage_key, target, mime_type, size, digest.hexdigest())
            raise StorageError("Generated asset download did not complete")
        except (httpx.RequestError, OSError) as exc:
            raise StorageError(f"Generated asset storage failed: {exc.__class__.__name__}") from exc
        finally:
            temporary.unlink(missing_ok=True)


def get_storage_adapter() -> StorageAdapter:
    return LocalStorageAdapter()
