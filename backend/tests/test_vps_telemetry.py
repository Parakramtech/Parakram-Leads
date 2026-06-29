"""Tests for the VPS telemetry + auto-update API."""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.api.v1.vps_telemetry import (
    HeartbeatStore,
    UpdateManifest,
    _build_update_manifest,
    _platform_matches,
    _sha256_from_checksums,
    get_current_user,
    get_store,
    is_newer,
    parse_version,
    router,
)

VALID_KEY = "ABCDE-FGHIJ-KLMNO-PQRST"
SHA = "a" * 64


def build_app(store: HeartbeatStore | None = None, user=None) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    if store is not None:
        app.dependency_overrides[get_store] = lambda: store
    if user is not None:
        app.dependency_overrides[get_current_user] = lambda: user
    return app


def client_for(app: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ─── Version helpers ──────────────────────────────────────────────────────

class TestVersionHelpers:
    def test_parse_basic(self):
        assert parse_version("2.1.0") == (2, 1, 0)

    def test_parse_with_v_prefix(self):
        assert parse_version("v2.1.0") == (2, 1, 0)

    def test_parse_pads_missing(self):
        assert parse_version("3") == (3, 0, 0)

    def test_parse_strips_suffix(self):
        assert parse_version("2.1.0-beta+build5") == (2, 1, 0)

    def test_is_newer_true(self):
        assert is_newer("2.1.0", "2.0.0") is True

    def test_is_newer_false_equal(self):
        assert is_newer("2.0.0", "2.0.0") is False

    def test_is_newer_false_older(self):
        assert is_newer("1.9.0", "2.0.0") is False


# ─── Platform / checksum helpers ────────────────────────────────────────────

class TestAssetHelpers:
    def test_windows_match(self):
        assert _platform_matches("ParakramVPS-Setup-2.1.0.exe", "windows") is True

    def test_windows_no_match_linux(self):
        assert _platform_matches("parakram-vps-linux-x64.tar.gz", "windows") is False

    def test_linux_match_targz(self):
        assert _platform_matches("parakram-vps-linux-x64.tar.gz", "linux") is True

    def test_linux_match_deb(self):
        assert _platform_matches("parakram-vps_2.1.0_amd64.deb", "linux") is True

    def test_sha_from_checksums(self):
        text = f"{SHA}  parakram-vps-linux-x64.tar.gz\n{'b'*64}  other.zip"
        assert _sha256_from_checksums(text, "parakram-vps-linux-x64.tar.gz") == SHA

    def test_sha_from_checksums_missing(self):
        assert _sha256_from_checksums("nothing here", "x.exe") == ""


# ─── HeartbeatStore (in-memory fallback) ────────────────────────────────────

class TestHeartbeatStore:
    @pytest.fixture
    def mem_store(self):
        store = HeartbeatStore()
        store._redis_failed = True  # force in-memory path
        return store

    async def test_record_and_get(self, mem_store):
        await mem_store.record("vps-1", {"vps_id": "vps-1", "version": "2.0.0"})
        got = await mem_store.get("vps-1")
        assert got["version"] == "2.0.0"
        assert "_stored_at" not in got

    async def test_get_missing(self, mem_store):
        assert await mem_store.get("nope") is None

    async def test_list_all(self, mem_store):
        await mem_store.record("a", {"vps_id": "a"})
        await mem_store.record("b", {"vps_id": "b"})
        ids = {r["vps_id"] for r in await mem_store.list_all()}
        assert ids == {"a", "b"}


# ─── POST /vps/heartbeat ────────────────────────────────────────────────────

class TestHeartbeatEndpoint:
    @pytest.fixture
    def store(self):
        s = HeartbeatStore()
        s._redis_failed = True
        return s

    async def test_requires_auth(self, store):
        app = build_app(store=store)
        async with client_for(app) as c:
            resp = await c.post("/api/v1/vps/heartbeat", json={"vps_id": "x"})
        assert resp.status_code == 401

    async def test_rejects_bad_license(self, store):
        app = build_app(store=store)
        async with client_for(app) as c:
            resp = await c.post(
                "/api/v1/vps/heartbeat",
                json={"vps_id": "x"},
                headers={"Authorization": "Bearer not-a-key"},
            )
        assert resp.status_code == 401

    async def test_accepts_valid_heartbeat(self, store):
        app = build_app(store=store)
        payload = {
            "vps_id": "vps-123",
            "version": "2.0.0",
            "metrics": {"cpu_percent": 12.5, "memory_percent": 40.0, "hostname": "box1"},
            "tunnel_active": True,
            "leads_backend_active": True,
        }
        with patch(
            "app.api.v1.vps_telemetry._build_update_manifest",
            new=AsyncMock(return_value=UpdateManifest(update_available=False)),
        ):
            async with client_for(app) as c:
                resp = await c.post(
                    "/api/v1/vps/heartbeat",
                    json=payload,
                    headers={"Authorization": f"Bearer {VALID_KEY}", "X-VPS-ID": "vps-123"},
                )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["vps_id"] == "vps-123"
        assert body["next_interval_seconds"] > 0
        stored = await store.get("vps-123")
        assert stored["version"] == "2.0.0"
        assert stored["license_prefix"] == VALID_KEY[:8]

    async def test_heartbeat_reports_update_available(self, store):
        app = build_app(store=store)
        with patch(
            "app.api.v1.vps_telemetry._build_update_manifest",
            new=AsyncMock(return_value=UpdateManifest(update_available=True, version="3.0.0")),
        ):
            async with client_for(app) as c:
                resp = await c.post(
                    "/api/v1/vps/heartbeat",
                    json={"vps_id": "v", "version": "2.0.0"},
                    headers={"Authorization": f"Bearer {VALID_KEY}"},
                )
        assert resp.json()["update_available"] is True


# ─── GET /vps/updates/latest ────────────────────────────────────────────────

def _release(tag="2.1.0", assets=None, body=""):
    return {
        "tag_name": tag,
        "body": body,
        "published_at": "2026-01-01T00:00:00Z",
        "assets": assets or [],
    }


def _mock_github(release, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = release
    client = AsyncMock()
    client.get = AsyncMock(return_value=resp)
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


class TestUpdatesEndpoint:
    async def test_rejects_bad_platform(self):
        app = build_app()
        async with client_for(app) as c:
            resp = await c.get("/api/v1/vps/updates/latest", params={"platform": "solaris"})
        assert resp.status_code == 400

    async def test_no_update_when_not_newer(self):
        release = _release(tag="2.0.0", assets=[
            {"name": "ParakramVPS-Setup-2.0.0.exe", "browser_download_url": "u", "size": 10},
        ])
        with patch("httpx.AsyncClient", return_value=_mock_github(release)):
            app = build_app()
            async with client_for(app) as c:
                resp = await c.get(
                    "/api/v1/vps/updates/latest",
                    params={"current_version": "2.0.0", "platform": "windows"},
                )
        assert resp.json()["update_available"] is False

    async def test_windows_update_available(self):
        body = f"Release notes\nSHA256: {SHA}  ParakramVPS-Setup-2.1.0.exe"
        release = _release(tag="v2.1.0", body=body, assets=[
            {"name": "ParakramVPS-Setup-2.1.0.exe", "browser_download_url": "https://dl/exe", "size": 999},
        ])
        with patch("httpx.AsyncClient", return_value=_mock_github(release)):
            app = build_app()
            async with client_for(app) as c:
                resp = await c.get(
                    "/api/v1/vps/updates/latest",
                    params={"current_version": "2.0.0", "platform": "windows"},
                )
        data = resp.json()
        assert data["update_available"] is True
        assert data["version"] == "2.1.0"
        assert data["download_url"] == "https://dl/exe"
        assert data["sha256"] == SHA

    async def test_linux_update_picks_linux_asset(self):
        release = _release(tag="2.1.0", assets=[
            {"name": "ParakramVPS-Setup-2.1.0.exe", "browser_download_url": "win", "size": 1},
            {"name": "parakram-vps-linux-x64.tar.gz", "browser_download_url": "lin", "size": 2},
        ])
        with patch("httpx.AsyncClient", return_value=_mock_github(release)):
            app = build_app()
            async with client_for(app) as c:
                resp = await c.get(
                    "/api/v1/vps/updates/latest",
                    params={"current_version": "2.0.0", "platform": "linux"},
                )
        data = resp.json()
        assert data["update_available"] is True
        assert data["download_url"] == "lin"

    async def test_github_error_returns_no_update(self):
        with patch("httpx.AsyncClient", return_value=_mock_github({}, status=404)):
            manifest = await _build_update_manifest("2.0.0", "windows")
        assert manifest.update_available is False


# ─── GET /vps/instances ─────────────────────────────────────────────────────

class TestInstancesEndpoint:
    async def test_lists_recorded_instances(self):
        store = HeartbeatStore()
        store._redis_failed = True
        await store.record("vps-1", {
            "vps_id": "vps-1", "version": "2.0.0", "received_at": "2026-01-02T00:00:00Z",
            "metrics": {"hostname": "h1", "cpu_percent": 5.0, "memory_percent": 10.0, "disk_percent": 20.0},
            "tunnel_active": True, "leads_backend_active": False,
        })
        app = build_app(store=store, user=MagicMock())
        async with client_for(app) as c:
            resp = await c.get("/api/v1/vps/instances")
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) == 1
        assert rows[0]["vps_id"] == "vps-1"
        assert rows[0]["hostname"] == "h1"
        assert rows[0]["online"] is True
