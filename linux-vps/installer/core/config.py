"""Configuration for the Linux VPS installer."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LinuxPaths:
    install_dir: Path = Path(os.getenv("PARAKRAM_VPS_INSTALL_DIR", "/opt/parakram-vps"))
    config_dir: Path = Path(os.getenv("PARAKRAM_VPS_CONFIG_DIR", Path.home() / ".config" / "parakram-vps"))
    service_name: str = "parakram-vps"


@dataclass
class LinuxSettings:
    api_base: str = os.getenv("PARAKRAM_API_BASE", "https://leads.getparakram.in/api/v1")
    update_repo: str = os.getenv("PARAKRAM_VPS_RELEASE_REPO", "Parakramtech/Parakram-Leads")
    heartbeat_interval_seconds: int = int(os.getenv("PARAKRAM_VPS_HEARTBEAT_INTERVAL_SECONDS", "60"))
    heartbeat_ttl_seconds: int = int(os.getenv("PARAKRAM_VPS_HEARTBEAT_TTL_SECONDS", "300"))
    version: str = os.getenv("PARAKRAM_VPS_VERSION", "2.0.0")


PATHS = LinuxPaths()
SETTINGS = LinuxSettings()
