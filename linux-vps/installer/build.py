"""Build script for the Linux VPS release bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).parent
DIST = ROOT / "dist"
MANIFEST = DIST / "build_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_bundle(version: str) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    bundle_root = DIST / f"parakram-vps-linux-{version}"
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir()

    for rel in ["app.py", "requirements.txt", "install.sh"]:
        shutil.copy2(ROOT / rel, bundle_root / rel)
    shutil.copytree(ROOT / "core", bundle_root / "core")

    archive = DIST / f"parakram-vps-linux-x64-{version}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(bundle_root, arcname=bundle_root.name)

    manifest = {"version": version, "artifacts": [{"name": archive.name, "sha256": sha256(archive), "size": archive.stat().st_size}]}
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="2.0.0")
    args = parser.parse_args()
    archive = build_bundle(args.version)
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
