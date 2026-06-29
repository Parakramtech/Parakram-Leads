"""Linux VPS agent entrypoint."""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from dataclasses import asdict
from pathlib import Path

import httpx

from core.config import PATHS, SETTINGS
from core.metrics import collect_metrics, metrics_to_dict
from core.service_manager import enable_service, render_service_file, write_service_file
from core.updater import LinuxAutoUpdater

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = PATHS.config_dir / "config.json"
SERVICE_FILE = PATHS.install_dir / "parakram-vps.service"
ENTRYPOINT = Path(__file__).resolve()


class HeartbeatClient:
    def __init__(self, vps_id: str, license_key: str) -> None:
        self.vps_id = vps_id
        self.license_key = license_key
        self.stop_event = threading.Event()

    def payload(self) -> dict:
        metrics = collect_metrics()
        return {
            "vps_id": self.vps_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": SETTINGS.version,
            "metrics": metrics_to_dict(metrics),
            "services": [],
            "tunnel_active": False,
            "tunnel_url": "",
            "leads_backend_active": False,
            "docker_running": False,
            "errors": [],
        }

    def send(self) -> bool:
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{SETTINGS.api_base}/vps/heartbeat",
                    json=self.payload(),
                    headers={"Authorization": f"Bearer {self.license_key}", "X-VPS-ID": self.vps_id},
                )
            return resp.status_code in (200, 201, 202)
        except Exception:
            return False

    def run(self) -> None:
        while not self.stop_event.is_set():
            self.send()
            self.stop_event.wait(SETTINGS.heartbeat_interval_seconds)


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {"vps_id": "unconfigured", "license_key": "", "current_version": SETTINGS.version}


def save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def install() -> int:
    PATHS.install_dir.mkdir(parents=True, exist_ok=True)
    config = load_config()
    write_service_file(SERVICE_FILE, "/usr/bin/python3", ENTRYPOINT)
    save_config(config)
    enable_service(SERVICE_FILE)
    logger.info("Installed Parakram VPS Linux service at %s", SERVICE_FILE)
    return 0


def run() -> int:
    config = load_config()
    updater = LinuxAutoUpdater(config.get("current_version"))
    updater.check_for_update()
    client = HeartbeatClient(config["vps_id"], config["license_key"])
    client.run()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("install", "run", "status", "render-service"))
    args = parser.parse_args()

    if args.command == "install":
        return install()
    if args.command == "run":
        return run()
    if args.command == "status":
        print(json.dumps(load_config(), indent=2))
        return 0
    if args.command == "render-service":
        print(render_service_file("/usr/bin/python3", ENTRYPOINT))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
