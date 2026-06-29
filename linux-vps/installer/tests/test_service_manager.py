import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.config import PATHS
from core.service_manager import disable_service, enable_service, render_service_file, write_service_file


def test_render_service_file_contains_entrypoint(tmp_path, monkeypatch):
    monkeypatch.setattr(PATHS, "install_dir", tmp_path, raising=False)
    rendered = render_service_file("/usr/bin/python3", Path("/opt/parakram-vps/app.py"))
    assert "ExecStart=/usr/bin/python3 /opt/parakram-vps/app.py run" in rendered


def test_write_service_file(tmp_path, monkeypatch):
    monkeypatch.setattr(PATHS, "install_dir", tmp_path, raising=False)
    dst = tmp_path / "parakram-vps.service"
    out = write_service_file(dst, "/usr/bin/python3", Path("/opt/parakram-vps/app.py"))
    assert out == dst
    assert dst.exists()


def test_enable_service_invokes_systemctl(tmp_path, monkeypatch):
    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)
        return MagicMock(returncode=0)

    with patch("core.service_manager.subprocess.run", side_effect=fake_run):
        enable_service(tmp_path / "parakram-vps.service")
    assert calls[0][:2] == ["systemctl", "daemon-reload"]


def test_disable_service_invokes_systemctl():
    with patch("core.service_manager.subprocess.run", return_value=MagicMock(returncode=0)) as run:
        disable_service()
    assert run.call_count == 3
