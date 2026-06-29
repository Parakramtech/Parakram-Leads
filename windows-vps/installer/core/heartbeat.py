"""
PARAKRAM VPS — HEARTBEAT & TELEMETRY
=======================================
Periodic health reporting to the Parakram backend so the platform
knows which VPS instances are alive, their resource usage, and service status.

Design:
  - Background daemon thread sends heartbeats every 60 seconds
  - Collects: CPU%, memory%, disk%, uptime, service status, network stats
  - Reports to Parakram Leads API with auth token
  - Graceful degradation: if backend unreachable, queue heartbeats locally
  - Respects circuit breaker: backs off on repeated failures
  - Persists last-known-good state for dashboard offline display

Usage:
    heartbeat = HeartbeatService(auth_token="...", vps_id="vps-xxx")
    heartbeat.start()  # Begins background reporting
    ...
    heartbeat.stop()   # Graceful shutdown
"""

import os
import sys
import json
import time
import logging
import threading
import platform
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

HEARTBEAT_ENDPOINT = "https://leads.getparakram.in/api/v1/vps/heartbeat"
HEARTBEAT_INTERVAL_SECONDS = 60
HEARTBEAT_TIMEOUT = 10
MAX_QUEUED_HEARTBEATS = 100
HEARTBEAT_STATE_FILE = "heartbeat_state.json"
MAX_CONSECUTIVE_FAILURES = 5
BACKOFF_BASE_SECONDS = 30
BACKOFF_MAX_SECONDS = 600


# ═══════════════════════════════════════════════════════════════════════════
#  DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SystemMetrics:
    """Snapshot of system resource usage."""
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


@dataclass
class ServiceStatus:
    """Status of a managed service."""
    name: str
    running: bool
    pid: Optional[int] = None
    uptime_seconds: Optional[int] = None
    port: Optional[int] = None
    health: str = "unknown"  # healthy, degraded, down, unknown


@dataclass
class HeartbeatPayload:
    """Full heartbeat payload sent to backend."""
    vps_id: str
    timestamp: str
    version: str
    metrics: SystemMetrics
    services: list[ServiceStatus] = field(default_factory=list)
    tunnel_active: bool = False
    tunnel_url: str = ""
    leads_backend_active: bool = False
    docker_running: bool = False
    errors: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
#  SYSTEM METRICS COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════

class MetricsCollector:
    """Collects system metrics using Windows-native APIs and WMI commands."""

    @staticmethod
    def collect() -> SystemMetrics:
        """Gather current system metrics. Gracefully degrades on access errors."""
        metrics = SystemMetrics()
        metrics.hostname = platform.node()
        metrics.platform_version = platform.version()

        # CPU usage via WMI (Windows) or /proc (fallback)
        metrics.cpu_percent = MetricsCollector._get_cpu_percent()

        # Memory
        mem_total, mem_used = MetricsCollector._get_memory()
        metrics.memory_total_mb = mem_total
        metrics.memory_used_mb = mem_used
        metrics.memory_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0.0

        # Disk
        disk_total, disk_used = MetricsCollector._get_disk()
        metrics.disk_total_gb = disk_total
        metrics.disk_used_gb = disk_used
        metrics.disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0.0

        # Uptime
        metrics.uptime_seconds = MetricsCollector._get_uptime()
        metrics.boot_time = MetricsCollector._get_boot_time()

        return metrics

    @staticmethod
    def _get_cpu_percent() -> float:
        """Get CPU usage percentage."""
        try:
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["wmic", "cpu", "get", "loadpercentage"],
                    capture_output=True, text=True, timeout=5,
                )
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line.isdigit():
                        return float(line)
            else:
                # Linux/macOS fallback for testing
                with open("/proc/stat", "r") as f:
                    line = f.readline()
                    parts = line.split()
                    idle = int(parts[4])
                    total = sum(int(p) for p in parts[1:])
                    return round((1 - idle / total) * 100, 1) if total > 0 else 0.0
        except Exception:
            pass
        return 0.0

    @staticmethod
    def _get_memory() -> tuple[int, int]:
        """Return (total_mb, used_mb)."""
        try:
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory"],
                    capture_output=True, text=True, timeout=5,
                )
                lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        free_kb = int(parts[0])
                        total_kb = int(parts[1])
                        return total_kb // 1024, (total_kb - free_kb) // 1024
            else:
                # Linux fallback
                with open("/proc/meminfo", "r") as f:
                    content = f.read()
                total = used = 0
                for line in content.split("\n"):
                    if line.startswith("MemTotal:"):
                        total = int(line.split()[1]) // 1024
                    elif line.startswith("MemAvailable:"):
                        available = int(line.split()[1]) // 1024
                        used = total - available
                return total, used
        except Exception:
            pass
        return 0, 0

    @staticmethod
    def _get_disk() -> tuple[float, float]:
        """Return (total_gb, used_gb) for system drive."""
        try:
            import shutil
            if sys.platform == "win32":
                drive = os.environ.get("SystemDrive", "C:")
            else:
                drive = "/"
            usage = shutil.disk_usage(drive)
            return round(usage.total / (1024**3), 1), round(usage.used / (1024**3), 1)
        except Exception:
            return 0.0, 0.0

    @staticmethod
    def _get_uptime() -> int:
        """Return system uptime in seconds."""
        try:
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["wmic", "os", "get", "LastBootUpTime"],
                    capture_output=True, text=True, timeout=5,
                )
                lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
                if len(lines) >= 2:
                    boot_str = lines[1][:14]  # YYYYMMDDHHmmss
                    boot_time = datetime(
                        int(boot_str[:4]), int(boot_str[4:6]),
                        int(boot_str[6:8]), int(boot_str[8:10]),
                        int(boot_str[10:12]), int(boot_str[12:14]),
                    )
                    delta = datetime.now() - boot_time
                    return int(delta.total_seconds())
            else:
                with open("/proc/uptime", "r") as f:
                    return int(float(f.read().split()[0]))
        except Exception:
            pass
        return 0

    @staticmethod
    def _get_boot_time() -> str:
        """Return boot time as ISO string."""
        uptime = MetricsCollector._get_uptime()
        if uptime > 0:
            boot = datetime.now(timezone.utc).timestamp() - uptime
            return datetime.fromtimestamp(boot, timezone.utc).isoformat()
        return ""


# ═══════════════════════════════════════════════════════════════════════════
#  SERVICE CHECKER
# ═══════════════════════════════════════════════════════════════════════════

class ServiceChecker:
    """Checks the status of VPS-managed services."""

    @staticmethod
    def check_all(config: dict) -> list[ServiceStatus]:
        """Check all managed services and return their statuses."""
        services = []

        # SSH Server
        services.append(ServiceChecker._check_windows_service("sshd", "OpenSSH Server"))

        # Dashboard Server
        dashboard_port = config.get("dashboard_port", 9876)
        services.append(ServiceChecker._check_http_service(
            "dashboard", "Management Dashboard", dashboard_port
        ))

        # Cloudflare Tunnel
        services.append(ServiceChecker._check_process("cloudflared", "Cloudflare Tunnel"))

        # Docker
        services.append(ServiceChecker._check_process("docker", "Docker Desktop"))

        return services

    @staticmethod
    def _check_windows_service(service_name: str, display_name: str) -> ServiceStatus:
        """Check if a Windows service is running."""
        status = ServiceStatus(name=display_name, running=False, health="down")
        try:
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True, text=True, timeout=5,
                )
                if "RUNNING" in result.stdout:
                    status.running = True
                    status.health = "healthy"
                elif "STOPPED" in result.stdout:
                    status.health = "down"
            else:
                status.health = "unknown"
        except Exception:
            status.health = "unknown"
        return status

    @staticmethod
    def _check_http_service(
        name: str, display_name: str, port: int
    ) -> ServiceStatus:
        """Check if an HTTP service responds on the given port."""
        status = ServiceStatus(name=display_name, running=False, port=port, health="down")
        try:
            with httpx.Client(timeout=3) as client:
                resp = client.get(f"http://localhost:{port}/")
                if resp.status_code < 500:
                    status.running = True
                    status.health = "healthy"
                else:
                    status.health = "degraded"
        except httpx.ConnectError:
            status.health = "down"
        except Exception:
            status.health = "unknown"
        return status

    @staticmethod
    def _check_process(process_name: str, display_name: str) -> ServiceStatus:
        """Check if a process is running by name."""
        status = ServiceStatus(name=display_name, running=False, health="down")
        try:
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {process_name}.exe", "/NH"],
                    capture_output=True, text=True, timeout=5,
                )
                if process_name.lower() in result.stdout.lower():
                    status.running = True
                    status.health = "healthy"
            else:
                import subprocess
                result = subprocess.run(
                    ["pgrep", "-f", process_name],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    status.running = True
                    status.health = "healthy"
        except Exception:
            status.health = "unknown"
        return status


# ═══════════════════════════════════════════════════════════════════════════
#  HEARTBEAT SERVICE
# ═══════════════════════════════════════════════════════════════════════════

class HeartbeatService:
    """
    Background daemon that periodically reports VPS health to the Parakram backend.

    Implements:
      - Exponential backoff on repeated failures
      - Local queue for offline resilience
      - Graceful shutdown with final heartbeat
    """

    def __init__(
        self,
        auth_token: str,
        vps_id: str,
        version: str = "2.0.0",
        install_dir: Optional[Path] = None,
        interval: int = HEARTBEAT_INTERVAL_SECONDS,
    ):
        self._auth_token = auth_token
        self._vps_id = vps_id
        self._version = version
        self._install_dir = install_dir or Path(
            os.environ.get("ProgramFiles", "C:\\Program Files")
        ) / "ParakramVPS"
        self._interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._consecutive_failures = 0
        self._queue: list[dict] = []
        self._last_successful_report: Optional[str] = None
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load VPS config from install directory."""
        config_path = self._install_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def last_successful_report(self) -> Optional[str]:
        return self._last_successful_report

    # ─── Lifecycle ─────────────────────────────────────────────────

    def start(self):
        """Start the heartbeat daemon thread."""
        if self.is_running:
            logger.warning("Heartbeat service already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="VPS-Heartbeat"
        )
        self._thread.start()
        logger.info(f"Heartbeat service started (interval={self._interval}s, vps_id={self._vps_id})")

    def stop(self):
        """Stop the heartbeat daemon gracefully. Sends final heartbeat."""
        if not self.is_running:
            return

        logger.info("Stopping heartbeat service...")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)

        # Final heartbeat
        try:
            self._send_heartbeat()
        except Exception:
            pass

    # ─── Main Loop ─────────────────────────────────────────────────

    def _run_loop(self):
        """Main heartbeat loop with backoff on failures."""
        # Initial delay to let services start
        self._stop_event.wait(5)

        while not self._stop_event.is_set():
            try:
                self._send_heartbeat()
                self._flush_queue()
                self._consecutive_failures = 0
            except Exception as e:
                self._consecutive_failures += 1
                logger.debug(
                    f"Heartbeat failed ({self._consecutive_failures}): {e}"
                )

            # Calculate sleep with backoff
            if self._consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                backoff = min(
                    BACKOFF_BASE_SECONDS * (2 ** (self._consecutive_failures - MAX_CONSECUTIVE_FAILURES)),
                    BACKOFF_MAX_SECONDS,
                )
                sleep_time = backoff
            else:
                sleep_time = self._interval

            self._stop_event.wait(sleep_time)

    # ─── Heartbeat Sending ─────────────────────────────────────────

    def _collect_payload(self) -> HeartbeatPayload:
        """Collect current system state into a heartbeat payload."""
        metrics = MetricsCollector.collect()
        services = ServiceChecker.check_all(self._config)

        # Determine tunnel status
        tunnel_active = any(s.running for s in services if "tunnel" in s.name.lower())
        tunnel_url = self._config.get("tunnel_url", "")

        # Determine leads backend status
        leads_active = False
        docker_running = any(s.running for s in services if "docker" in s.name.lower())
        if docker_running:
            leads_active = self._check_leads_backend()

        errors = []
        for svc in services:
            if svc.health == "down" and svc.name not in ("Docker Desktop",):
                errors.append(f"{svc.name} is not running")

        return HeartbeatPayload(
            vps_id=self._vps_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=self._version,
            metrics=metrics,
            services=services,
            tunnel_active=tunnel_active,
            tunnel_url=tunnel_url,
            leads_backend_active=leads_active,
            docker_running=docker_running,
            errors=errors,
        )

    def _check_leads_backend(self) -> bool:
        """Quick check if leads backend container is healthy."""
        try:
            with httpx.Client(timeout=3) as client:
                resp = client.get("http://localhost:8080/api/v1/health")
                return resp.status_code == 200
        except Exception:
            return False

    def _send_heartbeat(self):
        """Send a single heartbeat to the backend."""
        payload = self._collect_payload()

        # Serialize dataclasses to dict
        data = {
            "vps_id": payload.vps_id,
            "timestamp": payload.timestamp,
            "version": payload.version,
            "metrics": asdict(payload.metrics),
            "services": [asdict(s) for s in payload.services],
            "tunnel_active": payload.tunnel_active,
            "tunnel_url": payload.tunnel_url,
            "leads_backend_active": payload.leads_backend_active,
            "docker_running": payload.docker_running,
            "errors": payload.errors,
        }

        try:
            with httpx.Client(timeout=HEARTBEAT_TIMEOUT) as client:
                resp = client.post(
                    HEARTBEAT_ENDPOINT,
                    json=data,
                    headers={
                        "Authorization": f"Bearer {self._auth_token}",
                        "X-VPS-ID": self._vps_id,
                    },
                )
                if resp.status_code in (200, 201, 202):
                    self._last_successful_report = payload.timestamp
                    self._save_state(data)
                    return
                elif resp.status_code == 401:
                    logger.warning("Heartbeat auth failed — token may be expired")
                    raise RuntimeError("Authentication failed")
                else:
                    raise RuntimeError(f"HTTP {resp.status_code}")
        except httpx.ConnectError:
            # Backend unreachable — queue for later
            self._enqueue(data)
            raise
        except httpx.TimeoutException:
            self._enqueue(data)
            raise

    # ─── Queue Management ──────────────────────────────────────────

    def _enqueue(self, data: dict):
        """Add heartbeat to offline queue."""
        if len(self._queue) >= MAX_QUEUED_HEARTBEATS:
            self._queue.pop(0)  # Drop oldest
        self._queue.append(data)

    def _flush_queue(self):
        """Send queued heartbeats to backend."""
        if not self._queue:
            return

        sent = 0
        try:
            with httpx.Client(timeout=HEARTBEAT_TIMEOUT) as client:
                while self._queue:
                    data = self._queue[0]
                    resp = client.post(
                        HEARTBEAT_ENDPOINT,
                        json=data,
                        headers={
                            "Authorization": f"Bearer {self._auth_token}",
                            "X-VPS-ID": self._vps_id,
                        },
                    )
                    if resp.status_code in (200, 201, 202):
                        self._queue.pop(0)
                        sent += 1
                    else:
                        break
        except Exception:
            pass

        if sent > 0:
            logger.info(f"Flushed {sent} queued heartbeats")

    # ─── State Persistence ─────────────────────────────────────────

    def _save_state(self, data: dict):
        """Persist last-known-good state for offline dashboard display."""
        state_path = self._install_dir / HEARTBEAT_STATE_FILE
        try:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    @staticmethod
    def load_last_state(install_dir: Optional[Path] = None) -> Optional[dict]:
        """Load the last-known-good heartbeat state (for dashboard)."""
        install_dir = install_dir or Path(
            os.environ.get("ProgramFiles", "C:\\Program Files")
        ) / "ParakramVPS"
        state_path = install_dir / HEARTBEAT_STATE_FILE
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
