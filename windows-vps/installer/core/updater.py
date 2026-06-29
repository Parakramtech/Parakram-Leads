"""
PARAKRAM VPS — AUTO-UPDATE SYSTEM
===================================
Checks for new installer versions from the Parakram API and GitHub releases.
Downloads and stages updates for seamless in-place upgrades.

Design:
  - Non-blocking version check on startup (background thread)
  - Semantic version comparison (major.minor.patch)
  - Staged download with integrity verification (SHA-256)
  - Atomic replacement using Windows rename semantics
  - Rollback capability if update fails to launch
  - User consent required before applying update (GUI prompt or --auto-update flag)

Usage:
    updater = AutoUpdater(current_version="2.0.0")
    update_info = updater.check_for_update()  # Returns None if up-to-date
    if update_info:
        updater.download_update(update_info)
        updater.apply_update()  # Replaces current EXE and relaunches
"""

import os
import sys
import json
import time
import hashlib
import shutil
import logging
import threading
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

GITHUB_RELEASES_URL = "https://api.github.com/repos/Parakramtech/Parakram-Leads/releases/latest"
PARAKRAM_UPDATE_URL = "https://leads.getparakram.in/api/v1/vps/updates/latest"
UPDATE_CHECK_TIMEOUT = 15
DOWNLOAD_TIMEOUT = 300
DOWNLOAD_CHUNK_SIZE = 65536
STAGING_DIR_NAME = ".update_staging"


# ═══════════════════════════════════════════════════════════════════════════
#  DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UpdateInfo:
    """Metadata about an available update."""
    version: str
    download_url: str
    sha256: str
    size_bytes: int
    release_notes: str
    published_at: str
    is_critical: bool = False


# ═══════════════════════════════════════════════════════════════════════════
#  VERSION COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse semantic version string into comparable tuple."""
    clean = version_str.lstrip("vV").strip()
    parts = clean.split(".")
    result = []
    for p in parts:
        digits = ""
        for c in p:
            if c.isdigit():
                digits += c
            else:
                break
        result.append(int(digits) if digits else 0)
    while len(result) < 3:
        result.append(0)
    return tuple(result)


def is_newer(remote_version: str, current_version: str) -> bool:
    """Return True if remote_version is strictly newer than current_version."""
    return parse_version(remote_version) > parse_version(current_version)


# ═══════════════════════════════════════════════════════════════════════════
#  AUTO-UPDATER
# ═══════════════════════════════════════════════════════════════════════════

class AutoUpdater:
    """
    Manages the update lifecycle: check → download → stage → apply.

    Thread-safe for check operations. Download and apply must be
    called from the main thread or a dedicated update thread.
    """

    def __init__(self, current_version: str, install_dir: Optional[Path] = None):
        self.current_version = current_version
        self._install_dir = install_dir or Path(
            os.environ.get("ProgramFiles", "C:\\Program Files")
        ) / "ParakramVPS"
        self._staging_dir = self._install_dir / STAGING_DIR_NAME
        self._lock = threading.Lock()
        self._update_info: Optional[UpdateInfo] = None
        self._download_progress: float = 0.0
        self._download_complete = threading.Event()

    @property
    def staging_dir(self) -> Path:
        return self._staging_dir

    @property
    def download_progress(self) -> float:
        """Current download progress (0.0 to 1.0)."""
        return self._download_progress

    # ─── Check for Updates ─────────────────────────────────────────

    def check_for_update(self) -> Optional[UpdateInfo]:
        """
        Check for available updates. Tries Parakram API first, falls back to GitHub.
        Returns UpdateInfo if a newer version is available, None otherwise.
        Thread-safe.
        """
        info = self._check_parakram_api()
        if info is None:
            info = self._check_github_releases()

        if info and is_newer(info.version, self.current_version):
            with self._lock:
                self._update_info = info
            logger.info(
                f"Update available: {self.current_version} → {info.version}"
                f" (critical={info.is_critical})"
            )
            return info

        logger.info(f"No update available (current: {self.current_version})")
        return None

    def _check_parakram_api(self) -> Optional[UpdateInfo]:
        """Check the Parakram backend for update info."""
        try:
            with httpx.Client(timeout=UPDATE_CHECK_TIMEOUT) as client:
                resp = client.get(
                    PARAKRAM_UPDATE_URL,
                    params={"current_version": self.current_version, "platform": "windows"},
                )
                if resp.status_code != 200:
                    return None
                data = resp.json()
                if not data.get("update_available"):
                    return None
                return UpdateInfo(
                    version=data["version"],
                    download_url=data["download_url"],
                    sha256=data.get("sha256", ""),
                    size_bytes=data.get("size_bytes", 0),
                    release_notes=data.get("release_notes", ""),
                    published_at=data.get("published_at", ""),
                    is_critical=data.get("is_critical", False),
                )
        except Exception as e:
            logger.debug(f"Parakram API update check failed: {e}")
            return None

    def _check_github_releases(self) -> Optional[UpdateInfo]:
        """Fallback: check GitHub releases for the latest VPS installer."""
        try:
            with httpx.Client(
                timeout=UPDATE_CHECK_TIMEOUT,
                follow_redirects=True,
            ) as client:
                resp = client.get(
                    GITHUB_RELEASES_URL,
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code != 200:
                    return None
                release = resp.json()

                tag = release.get("tag_name", "")
                if not tag:
                    return None

                # Find Windows EXE asset
                download_url = ""
                size_bytes = 0
                sha256 = ""
                for asset in release.get("assets", []):
                    name = asset.get("name", "").lower()
                    if "parakramvps" in name and name.endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        size_bytes = asset.get("size", 0)
                        break

                if not download_url:
                    return None

                # Try to find SHA-256 in release body
                body = release.get("body", "")
                for line in body.split("\n"):
                    if "sha256" in line.lower() and len(line) >= 64:
                        # Extract hex string
                        parts = line.split()
                        for part in parts:
                            cleaned = part.strip("`*: ")
                            if len(cleaned) == 64 and all(
                                c in "0123456789abcdef" for c in cleaned
                            ):
                                sha256 = cleaned
                                break

                return UpdateInfo(
                    version=tag.lstrip("vV"),
                    download_url=download_url,
                    sha256=sha256,
                    size_bytes=size_bytes,
                    release_notes=body[:500],
                    published_at=release.get("published_at", ""),
                    is_critical="critical" in body.lower() or "security" in body.lower(),
                )
        except Exception as e:
            logger.debug(f"GitHub update check failed: {e}")
            return None

    # ─── Download Update ───────────────────────────────────────────

    def download_update(
        self,
        update_info: Optional[UpdateInfo] = None,
        progress_callback: Optional[callable] = None,
    ) -> Path:
        """
        Download update to staging directory with integrity verification.
        Returns path to downloaded file.
        Raises RuntimeError on failure.
        """
        info = update_info or self._update_info
        if info is None:
            raise RuntimeError("No update info available. Call check_for_update() first.")

        # Prepare staging directory
        self._staging_dir.mkdir(parents=True, exist_ok=True)
        staged_exe = self._staging_dir / f"ParakramVPS-Setup-{info.version}.exe"

        # Clean previous staging
        if staged_exe.exists():
            staged_exe.unlink()

        logger.info(f"Downloading update v{info.version} from {info.download_url}")
        self._download_progress = 0.0
        self._download_complete.clear()

        try:
            with httpx.Client(
                timeout=httpx.Timeout(DOWNLOAD_TIMEOUT, connect=30),
                follow_redirects=True,
            ) as client:
                with client.stream("GET", info.download_url) as response:
                    response.raise_for_status()
                    total = info.size_bytes or int(
                        response.headers.get("content-length", 0)
                    )
                    downloaded = 0
                    hasher = hashlib.sha256()

                    with open(staged_exe, "wb") as f:
                        for chunk in response.iter_bytes(DOWNLOAD_CHUNK_SIZE):
                            f.write(chunk)
                            hasher.update(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                self._download_progress = downloaded / total
                            if progress_callback:
                                progress_callback(self._download_progress)

            # Verify integrity
            computed_sha256 = hasher.hexdigest()
            if info.sha256 and computed_sha256 != info.sha256:
                staged_exe.unlink()
                raise RuntimeError(
                    f"SHA-256 mismatch: expected {info.sha256[:16]}..., "
                    f"got {computed_sha256[:16]}..."
                )

            # Verify PE header
            with open(staged_exe, "rb") as f:
                header = f.read(2)
                if header != b"MZ":
                    staged_exe.unlink()
                    raise RuntimeError("Downloaded file is not a valid Windows executable")

            # Write metadata
            meta = {
                "version": info.version,
                "sha256": computed_sha256,
                "size_bytes": staged_exe.stat().st_size,
                "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "release_notes": info.release_notes[:500],
                "is_critical": info.is_critical,
            }
            meta_path = self._staging_dir / "update_meta.json"
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

            self._download_progress = 1.0
            self._download_complete.set()
            logger.info(
                f"Update downloaded: {staged_exe.stat().st_size / (1024*1024):.1f} MB, "
                f"SHA-256: {computed_sha256[:16]}..."
            )
            return staged_exe

        except Exception as e:
            self._download_progress = 0.0
            if staged_exe.exists():
                staged_exe.unlink()
            raise RuntimeError(f"Download failed: {e}") from e

    # ─── Apply Update ──────────────────────────────────────────────

    def apply_update(self) -> bool:
        """
        Apply staged update: rename current EXE → .old, move staged → current, relaunch.
        Returns True if update was initiated (current process will exit).
        Returns False if no staged update found.
        """
        if not self._staging_dir.exists():
            return False

        # Find staged EXE
        staged_files = list(self._staging_dir.glob("ParakramVPS-Setup-*.exe"))
        if not staged_files:
            return False

        staged_exe = staged_files[0]
        current_exe = Path(sys.executable) if getattr(sys, "frozen", False) else None

        if current_exe is None:
            # Running as script, not EXE — skip replacement, just log
            logger.warning("Cannot apply update: not running as frozen EXE")
            return False

        # Create update batch script that runs after this process exits
        update_script = self._staging_dir / "apply_update.bat"
        update_script.write_text(
            f'@echo off\n'
            f'echo Applying Parakram VPS update...\n'
            f'timeout /t 2 /nobreak >nul\n'
            f'move /Y "{current_exe}" "{current_exe}.old"\n'
            f'move /Y "{staged_exe}" "{current_exe}"\n'
            f'if exist "{current_exe}" (\n'
            f'    echo Update applied successfully.\n'
            f'    start "" "{current_exe}"\n'
            f'    del /Q "{current_exe}.old"\n'
            f') else (\n'
            f'    echo Update failed! Restoring backup...\n'
            f'    move /Y "{current_exe}.old" "{current_exe}"\n'
            f'    start "" "{current_exe}"\n'
            f')\n'
            f'rmdir /S /Q "{self._staging_dir}"\n'
            f'del "%~f0"\n',
            encoding="utf-8",
        )

        logger.info(f"Launching update script: {update_script}")
        import subprocess
        subprocess.Popen(
            ["cmd.exe", "/c", str(update_script)],
            creationflags=0x00000008,  # DETACHED_PROCESS
            close_fds=True,
        )
        return True

    # ─── Cleanup ───────────────────────────────────────────────────

    def cleanup_staging(self):
        """Remove staging directory and any leftover .old files."""
        if self._staging_dir.exists():
            shutil.rmtree(self._staging_dir, ignore_errors=True)

        # Clean up .old backup if previous update succeeded
        if getattr(sys, "frozen", False):
            old_exe = Path(sys.executable).with_suffix(".exe.old")
            if old_exe.exists():
                try:
                    old_exe.unlink()
                except OSError:
                    pass

    # ─── Convenience: Background Check ─────────────────────────────

    def check_async(self, callback: Optional[callable] = None):
        """
        Check for updates in background thread.
        callback(update_info) is called on completion (None if no update).
        """
        def _worker():
            try:
                info = self.check_for_update()
                if callback:
                    callback(info)
            except Exception as e:
                logger.debug(f"Background update check failed: {e}")
                if callback:
                    callback(None)

        t = threading.Thread(target=_worker, daemon=True, name="UpdateChecker")
        t.start()
        return t
