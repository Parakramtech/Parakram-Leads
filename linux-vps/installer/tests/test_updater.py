import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.updater import LinuxAutoUpdater, UpdateInfo, is_newer


def test_version_compare():
    assert is_newer("2.1.0", "2.0.0") is True
    assert is_newer("1.9.9", "2.0.0") is False


def test_verify_download(tmp_path):
    path = tmp_path / "a.tar.gz"
    path.write_bytes(b"hello")
    updater = LinuxAutoUpdater("2.0.0")
    assert updater.verify_download(path, "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824") is True


def test_check_for_update_from_github(tmp_path):
    release = {
        "tag_name": "v2.1.0",
        "body": "Release notes",
        "published_at": "2026-01-01T00:00:00Z",
        "assets": [{"name": "parakram-vps-linux-x64.tar.gz", "browser_download_url": "https://example.com/a", "size": 10}],
    }
    resp = MagicMock(status_code=200)
    resp.json.return_value = release
    client = MagicMock()
    client.get.return_value = resp
    ctx = MagicMock()
    ctx.__enter__.return_value = client
    ctx.__exit__.return_value = False
    with patch("httpx.Client", return_value=ctx):
        updater = LinuxAutoUpdater("2.0.0")
        info = updater.check_for_update()
    assert isinstance(info, UpdateInfo)
    assert info.download_url == "https://example.com/a"
