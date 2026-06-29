"""Tests for core/updater.py — Auto-update system."""

import json
import threading
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from tempfile import TemporaryDirectory

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.updater import (
    AutoUpdater,
    UpdateInfo,
    parse_version,
    is_newer,
    GITHUB_RELEASES_URL,
    PARAKRAM_UPDATE_URL,
)


class TestVersionParsing(unittest.TestCase):
    """Tests for semantic version parsing and comparison."""

    def test_parse_simple_version(self):
        assert parse_version("2.0.0") == (2, 0, 0)

    def test_parse_version_with_v_prefix(self):
        assert parse_version("v2.1.0") == (2, 1, 0)

    def test_parse_version_with_V_prefix(self):
        assert parse_version("V1.5.3") == (1, 5, 3)

    def test_parse_version_with_suffix(self):
        assert parse_version("2.1.0-beta") == (2, 1, 0)

    def test_parse_version_short(self):
        assert parse_version("3.1") == (3, 1, 0)

    def test_parse_version_single(self):
        assert parse_version("5") == (5, 0, 0)

    def test_is_newer_true(self):
        assert is_newer("2.1.0", "2.0.0") is True

    def test_is_newer_false_same(self):
        assert is_newer("2.0.0", "2.0.0") is False

    def test_is_newer_false_older(self):
        assert is_newer("1.9.0", "2.0.0") is False

    def test_is_newer_patch_bump(self):
        assert is_newer("2.0.1", "2.0.0") is True

    def test_is_newer_major_bump(self):
        assert is_newer("3.0.0", "2.9.9") is True


class TestAutoUpdaterCheck(unittest.TestCase):
    """Tests for update checking logic."""

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.install_dir = Path(self.tmp_dir.name)
        self.updater = AutoUpdater(
            current_version="2.0.0",
            install_dir=self.install_dir,
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    @patch("core.updater.httpx.Client")
    def test_check_parakram_api_returns_update(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "update_available": True,
            "version": "2.1.0",
            "download_url": "https://example.com/installer.exe",
            "sha256": "a" * 64,
            "size_bytes": 50000000,
            "release_notes": "Bug fixes",
            "published_at": "2026-06-01T00:00:00Z",
            "is_critical": False,
        }
        mock_client.get.return_value = mock_response

        info = self.updater._check_parakram_api()
        assert info is not None
        assert info.version == "2.1.0"
        assert info.is_critical is False

    @patch("core.updater.httpx.Client")
    def test_check_parakram_api_no_update(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"update_available": False}
        mock_client.get.return_value = mock_response

        info = self.updater._check_parakram_api()
        assert info is None

    @patch("core.updater.httpx.Client")
    def test_check_parakram_api_error(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = Exception("Connection refused")

        info = self.updater._check_parakram_api()
        assert info is None

    @patch("core.updater.httpx.Client")
    def test_check_github_releases_finds_exe(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v2.2.0",
            "assets": [
                {
                    "name": "ParakramVPS-Setup-2.2.0.exe",
                    "browser_download_url": "https://github.com/releases/download/v2.2.0/ParakramVPS-Setup-2.2.0.exe",
                    "size": 60000000,
                }
            ],
            "body": "Release notes\nSHA256: " + "b" * 64,
            "published_at": "2026-06-15T00:00:00Z",
        }
        mock_client.get.return_value = mock_response

        info = self.updater._check_github_releases()
        assert info is not None
        assert info.version == "2.2.0"
        assert info.sha256 == "b" * 64
        assert info.size_bytes == 60000000

    @patch("core.updater.httpx.Client")
    def test_check_github_no_exe_asset(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v2.2.0",
            "assets": [{"name": "source.tar.gz", "browser_download_url": "https://example.com/source.tar.gz", "size": 1000}],
            "body": "No exe in this release",
            "published_at": "2026-06-15T00:00:00Z",
        }
        mock_client.get.return_value = mock_response

        info = self.updater._check_github_releases()
        assert info is None

    @patch("core.updater.httpx.Client")
    def test_check_for_update_returns_none_when_same_version(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "update_available": True,
            "version": "2.0.0",  # Same as current
            "download_url": "https://example.com/installer.exe",
            "sha256": "a" * 64,
            "size_bytes": 50000000,
            "release_notes": "",
            "published_at": "",
        }
        mock_client.get.return_value = mock_response

        info = self.updater.check_for_update()
        assert info is None

    @patch("core.updater.httpx.Client")
    def test_check_for_update_detects_critical(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "update_available": True,
            "version": "2.5.0",
            "download_url": "https://example.com/installer.exe",
            "sha256": "",
            "size_bytes": 0,
            "release_notes": "",
            "published_at": "",
            "is_critical": True,
        }
        mock_client.get.return_value = mock_response

        info = self.updater.check_for_update()
        assert info is not None
        assert info.is_critical is True


class TestAutoUpdaterDownload(unittest.TestCase):
    """Tests for update downloading logic."""

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.install_dir = Path(self.tmp_dir.name)
        self.updater = AutoUpdater(
            current_version="2.0.0",
            install_dir=self.install_dir,
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_download_raises_without_update_info(self):
        with self.assertRaises(RuntimeError) as ctx:
            self.updater.download_update()
        assert "No update info" in str(ctx.exception)

    @patch("core.updater.httpx.Client")
    def test_download_verifies_sha256(self, mock_client_cls):
        info = UpdateInfo(
            version="2.1.0",
            download_url="https://example.com/installer.exe",
            sha256="wrong_hash",
            size_bytes=4,
            release_notes="",
            published_at="",
        )
        # Mock streaming response
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {"content-length": "4"}
        # MZ header (valid PE start) + padding
        mock_response.iter_bytes.return_value = [b"MZ\x00\x00"]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_client.stream.return_value = mock_response

        with self.assertRaises(RuntimeError) as ctx:
            self.updater.download_update(info)
        assert "SHA-256 mismatch" in str(ctx.exception)

    @patch("core.updater.httpx.Client")
    def test_download_validates_pe_header(self, mock_client_cls):
        info = UpdateInfo(
            version="2.1.0",
            download_url="https://example.com/installer.exe",
            sha256="",  # Skip SHA check
            size_bytes=4,
            release_notes="",
            published_at="",
        )
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {"content-length": "4"}
        mock_response.iter_bytes.return_value = [b"BAAD"]  # Not MZ
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_client.stream.return_value = mock_response

        with self.assertRaises(RuntimeError) as ctx:
            self.updater.download_update(info)
        assert "not a valid Windows executable" in str(ctx.exception)


class TestAutoUpdaterApply(unittest.TestCase):
    """Tests for update application logic."""

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.install_dir = Path(self.tmp_dir.name)
        self.updater = AutoUpdater(
            current_version="2.0.0",
            install_dir=self.install_dir,
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_apply_returns_false_no_staging(self):
        assert self.updater.apply_update() is False

    def test_apply_returns_false_no_staged_exe(self):
        self.updater.staging_dir.mkdir(parents=True)
        assert self.updater.apply_update() is False

    def test_apply_returns_false_when_not_frozen(self):
        staging = self.updater.staging_dir
        staging.mkdir(parents=True)
        (staging / "ParakramVPS-Setup-2.1.0.exe").write_bytes(b"MZ" + b"\x00" * 100)

        # sys.frozen is not set when running as script
        result = self.updater.apply_update()
        assert result is False

    def test_cleanup_staging(self):
        staging = self.updater.staging_dir
        staging.mkdir(parents=True)
        (staging / "test.txt").write_text("test")
        assert staging.exists()

        self.updater.cleanup_staging()
        assert not staging.exists()


class TestAutoUpdaterAsync(unittest.TestCase):
    """Tests for background update checking."""

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.install_dir = Path(self.tmp_dir.name)
        self.updater = AutoUpdater(
            current_version="2.0.0",
            install_dir=self.install_dir,
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    @patch("core.updater.httpx.Client")
    def test_check_async_calls_callback(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client.get.return_value = mock_response

        callback_result = []

        def callback(info):
            callback_result.append(info)

        t = self.updater.check_async(callback=callback)
        t.join(timeout=5)

        assert len(callback_result) == 1
        assert callback_result[0] is None


if __name__ == "__main__":
    unittest.main()
