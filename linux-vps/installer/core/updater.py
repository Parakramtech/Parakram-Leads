"""Linux auto-updater."""

from __future__ import annotations

import hashlib
import logging
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from .config import SETTINGS

logger = logging.getLogger(__name__)

GITHUB_RELEASES_URL = f"https://api.github.com/repos/{SETTINGS.update_repo}/releases/latest"
UPDATE_URL = f"{SETTINGS.api_base}/vps/updates/latest"


@dataclass
class UpdateInfo:
    version: str
    download_url: str
    sha256: str = ""
    size_bytes: int = 0
    release_notes: str = ""
    published_at: str = ""
    is_critical: bool = False


def is_newer(remote: str, current: str) -> bool:
    def parse(v: str) -> tuple[int, int, int]:
        parts = [int("".join(ch for ch in piece if ch.isdigit()) or "0") for piece in v.lstrip("vV").split(".")[:3]]
        return tuple(parts + [0] * (3 - len(parts)))

    return parse(remote) > parse(current)


def _asset_matches(name: str) -> bool:
    lowered = name.lower()
    return lowered.endswith((".tar.gz", ".tgz", ".zip", ".deb", ".appimage")) or "linux" in lowered


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class LinuxAutoUpdater:
    def __init__(self, current_version: str | None = None) -> None:
        self.current_version = current_version or SETTINGS.version

    def check_for_update(self) -> Optional[UpdateInfo]:
        info = self._check_parakram_api() or self._check_github()
        if info and is_newer(info.version, self.current_version):
            return info
        return None

    def _check_parakram_api(self) -> Optional[UpdateInfo]:
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(UPDATE_URL, params={"current_version": self.current_version, "platform": "linux"})
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data.get("update_available"):
                return None
            return UpdateInfo(**{k: data.get(k, "") for k in UpdateInfo.__annotations__})
        except Exception:
            return None

    def _check_github(self) -> Optional[UpdateInfo]:
        try:
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                resp = client.get(GITHUB_RELEASES_URL, headers={"Accept": "application/vnd.github+json"})
            if resp.status_code != 200:
                return None
            release = resp.json()
            version = release.get("tag_name", "").lstrip("vV")
            asset = next((a for a in release.get("assets", []) if _asset_matches(a.get("name", ""))), None)
            if not asset:
                return None
            return UpdateInfo(
                version=version,
                download_url=asset.get("browser_download_url", ""),
                sha256="",
                size_bytes=asset.get("size", 0),
                release_notes=(release.get("body", "") or "")[:1000],
                published_at=release.get("published_at", ""),
                is_critical="critical" in (release.get("body", "") or "").lower(),
            )
        except Exception:
            return None

    def verify_download(self, archive: Path, expected_sha256: str) -> bool:
        return bool(expected_sha256) and _sha256(archive) == expected_sha256

    def unpack(self, archive: Path, destination: Path) -> Path:
        destination.mkdir(parents=True, exist_ok=True)
        if archive.suffixes[-2:] == [".tar", ".gz"] or archive.name.endswith(".tar.gz"):
            with tarfile.open(archive, "r:gz") as tar:
                tar.extractall(destination)
        return destination
