"""Linux system metrics collectors."""

from __future__ import annotations

import os
import socket
import time
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SystemMetrics:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: int = 0
    memory_total_mb: int = 0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    uptime_seconds: int = 0
    boot_time: str = ""
    platform_version: str = ""
    hostname: str = ""


def _read_proc_stat() -> float:
    try:
        with open("/proc/stat", "r", encoding="utf-8") as fh:
            parts = fh.readline().split()
        idle = int(parts[4])
        total = sum(int(p) for p in parts[1:])
        return round((1.0 - idle / total) * 100, 1) if total else 0.0
    except Exception:
        return 0.0


def _read_meminfo() -> tuple[int, int]:
    try:
        total = available = 0
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    available = int(line.split()[1]) // 1024
        used = max(total - available, 0)
        return total, used
    except Exception:
        return 0, 0


def _read_uptime() -> int:
    try:
        return int(float(Path("/proc/uptime").read_text().split()[0]))
    except Exception:
        return 0


def collect_metrics() -> SystemMetrics:
    total_mb, used_mb = _read_meminfo()
    try:
        disk = os.statvfs("/")
        total_gb = round((disk.f_frsize * disk.f_blocks) / (1024**3), 1)
        used_gb = round(((disk.f_blocks - disk.f_bfree) * disk.f_frsize) / (1024**3), 1)
        disk_percent = round((used_gb / total_gb) * 100, 1) if total_gb else 0.0
    except Exception:
        total_gb = used_gb = disk_percent = 0.0

    return SystemMetrics(
        cpu_percent=_read_proc_stat(),
        memory_percent=round((used_mb / total_mb) * 100, 1) if total_mb else 0.0,
        memory_used_mb=used_mb,
        memory_total_mb=total_mb,
        disk_percent=disk_percent,
        disk_used_gb=used_gb,
        disk_total_gb=total_gb,
        uptime_seconds=_read_uptime(),
        boot_time="",
        platform_version=os.uname().release,
        hostname=socket.gethostname(),
    )


def metrics_to_dict(metrics: SystemMetrics) -> dict:
    return asdict(metrics)
