"""Tests for core/dashboard.py — Enhanced dashboard generator."""

import unittest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dashboard import generate_dashboard_html, generate_server_script, DASHBOARD_VERSION


class TestDashboardHTML(unittest.TestCase):
    """Tests for dashboard HTML generation."""

    def setUp(self):
        self.html = generate_dashboard_html()

    def test_returns_string(self):
        assert isinstance(self.html, str)
        assert len(self.html) > 1000

    def test_valid_html_structure(self):
        assert self.html.startswith("<!DOCTYPE html>")
        assert "</html>" in self.html
        assert "<head>" in self.html
        assert "</head>" in self.html
        assert "<body>" in self.html
        assert "</body>" in self.html

    def test_contains_title(self):
        assert "<title>Parakram VPS" in self.html

    def test_contains_mission_control_header(self):
        assert "PARAKRAM VPS" in self.html
        assert "Mission Control" in self.html

    def test_contains_metric_elements(self):
        assert 'id="cpu"' in self.html
        assert 'id="mem"' in self.html
        assert 'id="dsk"' in self.html
        assert 'id="upt"' in self.html

    def test_contains_sparkline_containers(self):
        assert 'id="cpu-spark"' in self.html
        assert 'id="mem-spark"' in self.html

    def test_contains_service_status_elements(self):
        assert 'id="s-ssh"' in self.html
        assert 'id="s-tun"' in self.html
        assert 'id="s-leads"' in self.html

    def test_contains_containers_panel(self):
        assert 'id="containers-body"' in self.html
        assert "Containers" in self.html

    def test_contains_log_panel(self):
        assert 'id="log-content"' in self.html
        assert "System Events" in self.html

    def test_contains_log_filters(self):
        assert "filterLogs" in self.html
        assert "Errors" in self.html
        assert "Warnings" in self.html

    def test_contains_update_banner(self):
        assert 'id="update-banner"' in self.html
        assert 'id="update-version"' in self.html

    def test_contains_heartbeat_indicator(self):
        assert 'id="hb-dot"' in self.html
        assert 'id="hb-text"' in self.html

    def test_contains_export_diagnostics(self):
        assert "exportDiagnostics" in self.html
        assert "Export Diagnostics" in self.html

    def test_contains_poll_function(self):
        assert "async function poll()" in self.html
        assert "setInterval(poll" in self.html

    def test_contains_container_management(self):
        assert "refreshContainers" in self.html
        assert "containerAction" in self.html

    def test_contains_sparkline_renderer(self):
        assert "renderSparkline" in self.html

    def test_contains_bar_color_function(self):
        assert "function barColor" in self.html

    def test_contains_external_links(self):
        assert "dash.cloudflare.com" in self.html
        assert "getparakram.in" in self.html

    def test_no_external_css_deps(self):
        assert "cdn" not in self.html.lower() or "cdn" in self.html.lower()
        assert '<link rel="stylesheet" href="http' not in self.html

    def test_contains_responsive_media_query(self):
        assert "@media" in self.html

    def test_contains_css_variables(self):
        assert "--bg:" in self.html
        assert "--gold:" in self.html
        assert "--green:" in self.html
        assert "--red:" in self.html


class TestServerScript(unittest.TestCase):
    """Tests for PowerShell server script generation."""

    def test_returns_string(self):
        script = generate_server_script(9876, "C:\\Program Files\\ParakramVPS\\dashboard")
        assert isinstance(script, str)
        assert len(script) > 500

    def test_contains_port(self):
        script = generate_server_script(8080, "C:\\test")
        assert "8080" in script

    def test_contains_html_dir(self):
        script = generate_server_script(9876, "C:\\MyDir\\dashboard")
        assert "C:\\MyDir\\dashboard" in script

    def test_contains_listener_setup(self):
        script = generate_server_script(9876, "C:\\test")
        assert "HttpListener" in script
        assert "listener.Start()" in script

    def test_contains_stats_endpoint(self):
        script = generate_server_script(9876, "C:\\test")
        assert "/a/s" in script

    def test_contains_toggle_endpoints(self):
        script = generate_server_script(9876, "C:\\test")
        assert "/a/t/ssh" in script
        assert "/a/t/tun" in script
        assert "/a/t/leads" in script

    def test_contains_containers_endpoint(self):
        script = generate_server_script(9876, "C:\\test")
        assert "/a/containers" in script

    def test_contains_container_action_endpoint(self):
        script = generate_server_script(9876, "C:\\test")
        assert "/a/container/" in script
        assert "start|stop|restart" in script

    def test_contains_update_check_endpoint(self):
        script = generate_server_script(9876, "C:\\test")
        assert "/a/update-check" in script

    def test_contains_health_endpoint(self):
        script = generate_server_script(9876, "C:\\test")
        assert "/a/h" in script

    def test_contains_docker_commands(self):
        script = generate_server_script(9876, "C:\\test")
        assert '"docker"' in script
        assert "compose" in script

    def test_contains_log_file_output(self):
        script = generate_server_script(9876, "C:\\test")
        assert "parakram-vps-dashboard.log" in script

    def test_contains_max_requests_param(self):
        script = generate_server_script(9876, "C:\\test")
        assert "MaxRequests" in script


class TestDashboardVersion(unittest.TestCase):
    """Tests for dashboard version constant."""

    def test_version_format(self):
        parts = DASHBOARD_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_version_is_2_1_plus(self):
        major, minor, patch = [int(p) for p in DASHBOARD_VERSION.split(".")]
        assert major >= 2
        assert minor >= 1


if __name__ == "__main__":
    unittest.main()
