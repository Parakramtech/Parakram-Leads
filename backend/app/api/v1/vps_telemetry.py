"""
PARAKRAM VPS — TELEMETRY & UPDATES API
========================================
Server side of the VPS-for-Windows/Linux client features:

  - POST /vps/heartbeat        Ingest periodic health reports from VPS instances
  - GET  /vps/updates/latest   Serve the latest release manifest (Windows / Linux)
  - GET  /vps/instances        List recently-seen VPS instances (authenticated)

Design:
  - Heartbeats are stored in Redis with a TTL so the "fleet" view reflects only
    instances that are currently alive. If Redis is unavailable, an in-memory
    fallback keeps the endpoint functional for single-instance deployments.
  - Device auth uses the VPS license key (Bearer token). The key format is
    validated; durable per-key verification is delegated to the subscription
    system and can be tightened without changing the client contract.
  - The update manifest is derived from GitHub Releases of the configured repo
    and reshaped into the schema the installer's AutoUpdater expects.
"""

import json
import logging
import re
import time
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.config import settings
from app.models.user import User
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vps", tags=["vps"])


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

LICENSE_KEY_RE = re.compile(r"^[A-Z0-9]{5,8}(-[A-Z0-9]{5,8}){2,4}$")
SHA256_RE = re.compile(r"\b[0-9a-f]{64}\b")
SUPPORTED_PLATFORMS = {"windows", "linux"}
GITHUB_API = "https://api.github.com"
HEARTBEAT_KEY_PREFIX = "vps:hb:"
ACTIVE_SET_KEY = "vps:active"
MAX_PAYLOAD_ERRORS = 50


# ═══════════════════════════════════════════════════════════════════════════
#  SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class HeartbeatMetrics(BaseModel):
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: int = 0
    memory_total_mb: int = 0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    uptime_seconds: int = 0
    boot_time: str = ""
    platform_version: str = ""
    hostname: str = ""


class HeartbeatServiceStatus(BaseModel):
    name: str
    running: bool
    pid: Optional[int] = None
    uptime_seconds: Optional[int] = None
    port: Optional[int] = None
    health: str = "unknown"


class HeartbeatRequest(BaseModel):
    vps_id: str = Field(..., min_length=1, max_length=128)
    timestamp: str = ""
    version: str = ""
    metrics: HeartbeatMetrics = Field(default_factory=HeartbeatMetrics)
    services: list[HeartbeatServiceStatus] = Field(default_factory=list)
    tunnel_active: bool = False
    tunnel_url: str = ""
    leads_backend_active: bool = False
    docker_running: bool = False
    errors: list[str] = Field(default_factory=list, max_length=MAX_PAYLOAD_ERRORS)


class HeartbeatResponse(BaseModel):
    status: str
    vps_id: str
    received_at: str
    next_interval_seconds: int
    update_available: bool = False


class UpdateManifest(BaseModel):
    update_available: bool
    version: str = ""
    download_url: str = ""
    sha256: str = ""
    size_bytes: int = 0
    release_notes: str = ""
    published_at: str = ""
    is_critical: bool = False


class VpsInstanceSummary(BaseModel):
    vps_id: str
    version: str
    hostname: str
    last_seen: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    tunnel_active: bool
    leads_backend_active: bool
    online: bool


# ═══════════════════════════════════════════════════════════════════════════
#  HEARTBEAT STORE (Redis-backed with in-memory fallback)
# ═══════════════════════════════════════════════════════════════════════════

class HeartbeatStore:
    """Persists the latest heartbeat per VPS instance with a TTL."""

    def __init__(self) -> None:
        self._redis = None
        self._redis_failed = False
        self._memory: dict[str, dict] = {}

    async def _get_redis(self):
        if self._redis is None and not self._redis_failed:
            try:
                from redis.asyncio import from_url
                self._redis = await from_url(settings.REDIS_URL, decode_responses=True)
                await self._redis.ping()
            except Exception as e:
                logger.warning(f"VPS telemetry Redis unavailable, using in-memory store: {e}")
                self._redis_failed = True
                self._redis = None
        return self._redis

    def _prune_memory(self) -> None:
        ttl = settings.VPS_HEARTBEAT_TTL_SECONDS
        now = time.time()
        expired = [k for k, v in self._memory.items() if now - v.get("_stored_at", 0) > ttl]
        for k in expired:
            del self._memory[k]

    async def record(self, vps_id: str, data: dict) -> None:
        ttl = settings.VPS_HEARTBEAT_TTL_SECONDS
        redis = await self._get_redis()
        if redis is not None:
            try:
                key = f"{HEARTBEAT_KEY_PREFIX}{vps_id}"
                await redis.set(key, json.dumps(data), ex=ttl)
                await redis.sadd(ACTIVE_SET_KEY, vps_id)
                return
            except Exception as e:
                logger.warning(f"VPS telemetry Redis write failed, falling back to memory: {e}")
                self._redis_failed = True
        self._memory[vps_id] = {**data, "_stored_at": time.time()}

    async def get(self, vps_id: str) -> Optional[dict]:
        redis = await self._get_redis()
        if redis is not None:
            try:
                raw = await redis.get(f"{HEARTBEAT_KEY_PREFIX}{vps_id}")
                return json.loads(raw) if raw else None
            except Exception:
                pass
        self._prune_memory()
        entry = self._memory.get(vps_id)
        return {k: v for k, v in entry.items() if k != "_stored_at"} if entry else None

    async def list_all(self) -> list[dict]:
        redis = await self._get_redis()
        if redis is not None:
            try:
                ids = await redis.smembers(ACTIVE_SET_KEY)
                result = []
                for vps_id in ids:
                    raw = await redis.get(f"{HEARTBEAT_KEY_PREFIX}{vps_id}")
                    if raw:
                        result.append(json.loads(raw))
                    else:
                        await redis.srem(ACTIVE_SET_KEY, vps_id)
                return result
            except Exception:
                pass
        self._prune_memory()
        return [{k: v for k, v in e.items() if k != "_stored_at"} for e in self._memory.values()]


_store = HeartbeatStore()


def get_store() -> HeartbeatStore:
    """Dependency hook so tests can override the heartbeat store."""
    return _store


# ═══════════════════════════════════════════════════════════════════════════
#  DEVICE AUTH
# ═══════════════════════════════════════════════════════════════════════════

def _extract_license_key(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail={"detail": "Missing or malformed Authorization header", "code": "AUTH_REQUIRED"},
        )
    token = authorization.split(" ", 1)[1].strip().upper()
    if not LICENSE_KEY_RE.match(token):
        raise HTTPException(
            status_code=401,
            detail={"detail": "Invalid license key", "code": "INVALID_LICENSE"},
        )
    return token


# ═══════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/heartbeat", response_model=HeartbeatResponse)
async def ingest_heartbeat(
    payload: HeartbeatRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
    x_vps_id: Optional[str] = Header(None, alias="X-VPS-ID"),
    store: HeartbeatStore = Depends(get_store),
):
    """Ingest a heartbeat from a VPS instance and store its latest state."""
    license_key = _extract_license_key(authorization)

    received_at = _utc_now_iso()
    record = {
        **payload.model_dump(),
        "license_prefix": license_key[:8],
        "received_at": received_at,
        "source_ip": request.client.host if request.client else "",
    }
    await store.record(payload.vps_id, record)

    logger.info(
        "VPS heartbeat received",
        extra={
            "vps_id": payload.vps_id,
            "version": payload.version,
            "cpu": payload.metrics.cpu_percent,
            "mem": payload.metrics.memory_percent,
            "tunnel": payload.tunnel_active,
            "leads": payload.leads_backend_active,
            "license_prefix": license_key[:8],
        },
    )

    update_available = False
    if payload.version:
        platform = "windows" if payload.metrics.platform_version and "linux" not in payload.metrics.platform_version.lower() else "linux"
        try:
            manifest = await _build_update_manifest(payload.version, platform)
            update_available = manifest.update_available
        except Exception:
            update_available = False

    return HeartbeatResponse(
        status="ok",
        vps_id=payload.vps_id,
        received_at=received_at,
        next_interval_seconds=settings.VPS_HEARTBEAT_INTERVAL_SECONDS,
        update_available=update_available,
    )


@router.get("/updates/latest", response_model=UpdateManifest)
async def latest_update(
    current_version: str = Query("0.0.0", max_length=32),
    platform: str = Query("windows", max_length=16),
):
    """Return the latest available update for the given platform, if newer."""
    platform = platform.strip().lower()
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail={"detail": f"Unsupported platform '{platform}'", "code": "BAD_PLATFORM"},
        )
    return await _build_update_manifest(current_version, platform)


@router.get("/instances", response_model=list[VpsInstanceSummary])
async def list_instances(
    current_user: User = Depends(get_current_user),
    store: HeartbeatStore = Depends(get_store),
):
    """List VPS instances seen within the heartbeat TTL window."""
    records = await store.list_all()
    summaries: list[VpsInstanceSummary] = []
    for r in records:
        metrics = r.get("metrics", {}) or {}
        summaries.append(
            VpsInstanceSummary(
                vps_id=r.get("vps_id", ""),
                version=r.get("version", ""),
                hostname=metrics.get("hostname", ""),
                last_seen=r.get("received_at", ""),
                cpu_percent=metrics.get("cpu_percent", 0.0),
                memory_percent=metrics.get("memory_percent", 0.0),
                disk_percent=metrics.get("disk_percent", 0.0),
                tunnel_active=r.get("tunnel_active", False),
                leads_backend_active=r.get("leads_backend_active", False),
                online=True,
            )
        )
    summaries.sort(key=lambda s: s.last_seen, reverse=True)
    return summaries


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a semantic version string into a comparable tuple."""
    cleaned = version_str.strip().lstrip("vV").split("-")[0].split("+")[0]
    parts: list[int] = []
    for piece in cleaned.split("."):
        digits = "".join(c for c in piece if c.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer(remote: str, current: str) -> bool:
    """Return True if remote version is strictly newer than current."""
    try:
        return parse_version(remote) > parse_version(current)
    except Exception:
        return False


def _platform_matches(asset_name: str, platform: str) -> bool:
    name = asset_name.lower()
    if platform == "windows":
        return name.endswith(".exe") and "parakram" in name
    if platform == "linux":
        return name.endswith((".tar.gz", ".appimage", ".deb")) or "linux" in name
    return False


def _sha256_from_checksums(text: str, asset_name: str) -> str:
    for line in text.splitlines():
        if asset_name.lower() in line.lower():
            match = SHA256_RE.search(line.lower())
            if match:
                return match.group(0)
    return ""


async def _build_update_manifest(current_version: str, platform: str) -> UpdateManifest:
    """Query GitHub Releases and reshape the latest release into a manifest."""
    repo = settings.VPS_RELEASE_REPO
    headers = {"Accept": "application/vnd.github+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(f"{GITHUB_API}/repos/{repo}/releases/latest", headers=headers)
            if resp.status_code != 200:
                logger.info(f"No GitHub release manifest (status {resp.status_code})")
                return UpdateManifest(update_available=False)
            release = resp.json()
    except Exception as e:
        logger.warning(f"Update manifest fetch failed: {e}")
        return UpdateManifest(update_available=False)

    tag = release.get("tag_name", "")
    version = tag.lstrip("vV")
    if not version or not is_newer(version, current_version):
        return UpdateManifest(update_available=False, version=version)

    assets = release.get("assets", [])
    download_url = ""
    size_bytes = 0
    asset_name = ""
    for asset in assets:
        if _platform_matches(asset.get("name", ""), platform):
            download_url = asset.get("browser_download_url", "")
            size_bytes = asset.get("size", 0)
            asset_name = asset.get("name", "")
            break

    if not download_url:
        return UpdateManifest(update_available=False, version=version)

    body = release.get("body", "") or ""
    sha256 = ""
    for asset in assets:
        name = asset.get("name", "").lower()
        if name in ("checksums.txt", "sha256sums", "sha256sums.txt"):
            try:
                async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                    csum = await client.get(asset.get("browser_download_url", ""), headers=headers)
                    if csum.status_code == 200:
                        sha256 = _sha256_from_checksums(csum.text, asset_name)
            except Exception:
                pass
            break
    if not sha256:
        sha256 = _sha256_from_checksums(body, asset_name)

    return UpdateManifest(
        update_available=True,
        version=version,
        download_url=download_url,
        sha256=sha256,
        size_bytes=size_bytes,
        release_notes=body[:1000],
        published_at=release.get("published_at", ""),
        is_critical=("critical" in body.lower() or "security" in body.lower()),
    )
