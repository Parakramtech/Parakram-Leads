import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.metrics import collect_metrics, metrics_to_dict, SystemMetrics


def test_metrics_to_dict_round_trip():
    metrics = SystemMetrics(hostname="box", cpu_percent=12.5, memory_total_mb=1024, memory_used_mb=256)
    data = metrics_to_dict(metrics)
    assert data["hostname"] == "box"
    assert data["cpu_percent"] == 12.5


def test_collect_metrics_returns_hostname():
    metrics = collect_metrics()
    assert metrics.hostname
    assert isinstance(metrics.platform_version, str)
