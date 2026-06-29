"""systemd service helpers for Linux VPS."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .config import PATHS


SERVICE_TEMPLATE = """[Unit]
Description=Parakram VPS
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={workdir}
ExecStart={python} {entrypoint} run
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""


def render_service_file(python: str, entrypoint: Path) -> str:
    return SERVICE_TEMPLATE.format(workdir=PATHS.install_dir, python=python, entrypoint=entrypoint)


def write_service_file(destination: Path, python: str, entrypoint: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_service_file(python, entrypoint), encoding="utf-8")
    return destination


def systemctl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["systemctl", *args], capture_output=True, text=True, check=False)


def enable_service(unit_file: Path) -> subprocess.CompletedProcess:
    systemctl("daemon-reload")
    systemctl("enable", unit_file.name)
    return systemctl("restart", unit_file.name)


def disable_service(unit_name: str = "parakram-vps.service") -> subprocess.CompletedProcess:
    systemctl("stop", unit_name)
    systemctl("disable", unit_name)
    return systemctl("daemon-reload")
