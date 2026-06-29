import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app
from core.metrics import SystemMetrics


def test_load_config_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config.json", raising=False)
    data = app.load_config()
    assert data["vps_id"] == "unconfigured"


def test_save_and_load_config(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config.json", raising=False)
    cfg = {"vps_id": "abc", "license_key": "key", "current_version": "2.0.0"}
    app.save_config(cfg)
    assert json.loads((tmp_path / "config.json").read_text())["vps_id"] == "abc"


def test_heartbeat_payload_contains_core_fields(monkeypatch):
    monkeypatch.setattr(app.SETTINGS, "version", "2.0.0", raising=False)
    client = app.HeartbeatClient("vps-1", "LICENSE")
    with patch("app.collect_metrics") as collect_metrics:
        collect_metrics.return_value = SystemMetrics(hostname="box")
        payload = client.payload()
    assert payload["vps_id"] == "vps-1"
    assert payload["version"] == "2.0.0"
    assert "metrics" in payload
