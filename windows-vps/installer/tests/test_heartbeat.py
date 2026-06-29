"""Tests for core/heartbeat.py — Heartbeat & telemetry system."""

import json
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from tempfile import TemporaryDirectory
from dataclasses import asdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.heartbeat import (
    HeartbeatService,
    MetricsCollector,
    ServiceChecker,
    SystemMetrics,
    ServiceStatus,
    HeartbeatPayload,
    HEARTBEAT_STATE_FILE,
)


class TestSystemMetrics(unittest.TestCase):
    """Tests for system metrics collection."""

    def test_metrics_dataclass_defaults(self):
        m = SystemMetrics()
        assert m.cpu_percent == 0.0
        assert m.memory_percent == 0.0
        assert m.memory_used_mb == 0
        assert m.memory_total_mb == 0
        assert m.disk_percent == 0.0
        assert m.uptime_seconds == 0
        assert m.hostname == ""

    @patch("core.heartbeat.sys.platform", "linux")
    def test_collect_returns_metrics(self):
        metrics = MetricsCollector.collect()
        assert isinstance(metrics, SystemMetrics)
        assert metrics.hostname != ""

    @patch("core.heartbeat.sys.platform", "linux")
    def test_get_disk_returns_tuple(self):
        total, used = MetricsCollector._get_disk()
        assert isinstance(total, float)
        assert isinstance(used, float)
        assert total >= 0
        assert used >= 0

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_get_cpu_windows(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="LoadPercentage\n45\n", returncode=0
        )
        cpu = MetricsCollector._get_cpu_percent()
        assert cpu == 45.0

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_get_cpu_windows_error(self, mock_run):
        mock_run.side_effect = Exception("WMI failed")
        cpu = MetricsCollector._get_cpu_percent()
        assert cpu == 0.0

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_get_memory_windows(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="FreePhysicalMemory  TotalVisibleMemorySize\n4194304  16777216\n",
            returncode=0,
        )
        total, used = MetricsCollector._get_memory()
        # 16777216 KB = 16384 MB total, 4194304 KB = 4096 MB free
        assert total == 16777216 // 1024
        assert used == (16777216 - 4194304) // 1024

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_get_uptime_windows(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="LastBootUpTime\n20260625120000.000000+000\n", returncode=0
        )
        uptime = MetricsCollector._get_uptime()
        assert isinstance(uptime, int)


class TestServiceChecker(unittest.TestCase):
    """Tests for service status checking."""

    def test_service_status_dataclass(self):
        s = ServiceStatus(name="Test", running=True, health="healthy")
        assert s.name == "Test"
        assert s.running is True
        assert s.health == "healthy"
        assert s.pid is None
        assert s.port is None

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_check_windows_service_running(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="SERVICE_NAME: sshd\n    STATE: 4  RUNNING\n", returncode=0
        )
        status = ServiceChecker._check_windows_service("sshd", "OpenSSH Server")
        assert status.running is True
        assert status.health == "healthy"

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_check_windows_service_stopped(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="SERVICE_NAME: sshd\n    STATE: 1  STOPPED\n", returncode=0
        )
        status = ServiceChecker._check_windows_service("sshd", "OpenSSH Server")
        assert status.running is False
        assert status.health == "down"

    @patch("core.heartbeat.httpx.Client")
    def test_check_http_service_healthy(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get.return_value = mock_response

        status = ServiceChecker._check_http_service("dash", "Dashboard", 9876)
        assert status.running is True
        assert status.health == "healthy"
        assert status.port == 9876

    @patch("core.heartbeat.httpx.Client")
    def test_check_http_service_down(self, mock_client_cls):
        import httpx
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        status = ServiceChecker._check_http_service("dash", "Dashboard", 9876)
        assert status.running is False
        assert status.health == "down"

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_check_process_running(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="cloudflared.exe   1234 Console   0   45,000 K\n",
            returncode=0,
        )
        status = ServiceChecker._check_process("cloudflared", "Cloudflare Tunnel")
        assert status.running is True
        assert status.health == "healthy"

    @patch("core.heartbeat.sys.platform", "win32")
    @patch("subprocess.run")
    def test_check_process_not_running(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="INFO: No tasks are running which match the specified criteria.\n",
            returncode=0,
        )
        status = ServiceChecker._check_process("cloudflared", "Cloudflare Tunnel")
        assert status.running is False
        assert status.health == "down"

    def test_check_all_returns_list(self):
        config = {"dashboard_port": 9876}
        with patch.object(ServiceChecker, "_check_windows_service") as mock_ws, \
             patch.object(ServiceChecker, "_check_http_service") as mock_http, \
             patch.object(ServiceChecker, "_check_process") as mock_proc:
            mock_ws.return_value = ServiceStatus(name="SSH", running=True, health="healthy")
            mock_http.return_value = ServiceStatus(name="Dashboard", running=True, health="healthy", port=9876)
            mock_proc.return_value = ServiceStatus(name="Test", running=False, health="down")

            services = ServiceChecker.check_all(config)
            assert len(services) == 4
            assert all(isinstance(s, ServiceStatus) for s in services)


class TestHeartbeatPayload(unittest.TestCase):
    """Tests for heartbeat payload construction."""

    def test_payload_serialization(self):
        payload = HeartbeatPayload(
            vps_id="vps-test",
            timestamp="2026-06-29T00:00:00Z",
            version="2.0.0",
            metrics=SystemMetrics(cpu_percent=45.0, memory_percent=60.0),
            services=[ServiceStatus(name="SSH", running=True, health="healthy")],
            tunnel_active=True,
            tunnel_url="https://test.getparakram.in",
        )
        data = asdict(payload)
        assert data["vps_id"] == "vps-test"
        assert data["metrics"]["cpu_percent"] == 45.0
        assert len(data["services"]) == 1
        assert data["tunnel_active"] is True


class TestHeartbeatService(unittest.TestCase):
    """Tests for the heartbeat service lifecycle."""

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.install_dir = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_init_state(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        assert svc.is_running is False
        assert svc.last_successful_report is None

    def test_start_and_stop(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
            interval=1,
        )

        with patch.object(svc, "_send_heartbeat"):
            svc.start()
            assert svc.is_running is True

            svc.stop()
            time.sleep(0.5)
            assert svc.is_running is False

    def test_start_twice_no_error(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
            interval=60,
        )
        with patch.object(svc, "_send_heartbeat"):
            svc.start()
            svc.start()  # Should not raise
            svc.stop()

    @patch("core.heartbeat.httpx.Client")
    @patch("core.heartbeat.MetricsCollector.collect")
    @patch("core.heartbeat.ServiceChecker.check_all")
    def test_send_heartbeat_success(self, mock_check_all, mock_collect, mock_client_cls):
        mock_collect.return_value = SystemMetrics(cpu_percent=50.0)
        mock_check_all.return_value = []

        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        svc._send_heartbeat()
        assert svc.last_successful_report is not None

    @patch("core.heartbeat.httpx.Client")
    @patch("core.heartbeat.MetricsCollector.collect")
    @patch("core.heartbeat.ServiceChecker.check_all")
    def test_send_heartbeat_auth_failure(self, mock_check_all, mock_collect, mock_client_cls):
        mock_collect.return_value = SystemMetrics()
        mock_check_all.return_value = []

        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.post.return_value = mock_response

        svc = HeartbeatService(
            auth_token="bad-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        with self.assertRaises(RuntimeError):
            svc._send_heartbeat()

    @patch("core.heartbeat.httpx.Client")
    @patch("core.heartbeat.MetricsCollector.collect")
    @patch("core.heartbeat.ServiceChecker.check_all")
    def test_send_heartbeat_queues_on_connection_error(self, mock_check_all, mock_collect, mock_client_cls):
        import httpx
        mock_collect.return_value = SystemMetrics()
        mock_check_all.return_value = []

        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = httpx.ConnectError("No route")

        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        with self.assertRaises(httpx.ConnectError):
            svc._send_heartbeat()
        assert len(svc._queue) == 1

    def test_enqueue_respects_max(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        for i in range(150):
            svc._enqueue({"index": i})
        assert len(svc._queue) == 100
        assert svc._queue[0]["index"] == 50  # Oldest dropped

    def test_save_and_load_state(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        test_data = {"vps_id": "vps-test", "metrics": {"cpu": 50}}
        svc._save_state(test_data)

        loaded = HeartbeatService.load_last_state(self.install_dir)
        assert loaded is not None
        assert loaded["vps_id"] == "vps-test"

    def test_load_last_state_missing_file(self):
        loaded = HeartbeatService.load_last_state(self.install_dir)
        assert loaded is None

    def test_load_config_missing_file(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        assert svc._config == {}

    def test_load_config_existing_file(self):
        config_path = self.install_dir / "config.json"
        config_path.write_text(json.dumps({"dashboard_port": 9876}))
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        assert svc._config["dashboard_port"] == 9876


class TestHeartbeatFlush(unittest.TestCase):
    """Tests for queue flushing logic."""

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.install_dir = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    @patch("core.heartbeat.httpx.Client")
    def test_flush_queue_sends_all(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        svc._queue = [{"data": 1}, {"data": 2}, {"data": 3}]
        svc._flush_queue()
        assert len(svc._queue) == 0

    @patch("core.heartbeat.httpx.Client")
    def test_flush_queue_partial_failure(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        responses = [MagicMock(status_code=200), MagicMock(status_code=500)]
        mock_client.post.side_effect = responses

        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        svc._queue = [{"data": 1}, {"data": 2}]
        svc._flush_queue()
        assert len(svc._queue) == 1  # Second item still in queue

    def test_flush_empty_queue(self):
        svc = HeartbeatService(
            auth_token="test-token",
            vps_id="vps-test",
            install_dir=self.install_dir,
        )
        svc._flush_queue()  # Should not raise
        assert len(svc._queue) == 0


if __name__ == "__main__":
    unittest.main()
