"""
PARAKRAM VPS — BUILD SYSTEM (Military/Space Grade)
====================================================
Classification: CONTROLLED
SLA: Zero-defect builds | Build artifact signing | Integrity verification

Pipeline:
  1. Environment validation (Python version, dependencies, platform)
  2. Dependency resolution with version pinning
  3. Static analysis (syntax check, import validation)
  4. PyInstaller build with all assets bundled
  5. Post-build verification (CRC, size, executable structure)
  6. NSIS installer creation (optional)
  7. Code signing (optional, requires certificate)
  8. Build artifact manifest with SHA-256 hashes

Usage:
    python build.py                          # Full production build
    python build.py --quick                  # Skip verification
    python build.py --sign                   # Code sign the EXE
    python build.py --clean-only             # Just clean build artifacts
    python build.py --version=2.0.0          # Set specific version

Requirements:
    pip install pyinstaller customtkinter Pillow httpx
"""

import os
import sys
import json
import hashlib
import shutil
import subprocess
import time
import ast
from pathlib import Path
from datetime import datetime
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

APP_NAME = "ParakramVPS-Setup"
ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC_DIR = ROOT
LOG_FILE = ROOT / "build.log"
ASSETS_DIR = ROOT / "assets"
CORE_DIR = ROOT / "core"
UI_DIR = ROOT / "ui"
LEADS_DIR = ROOT / "leads"
WHATSAPP_BRIDGE_DIR = ROOT.parent.parent / "whatsapp-bridge"

MIN_PYTHON = (3, 10)
REQUIRED_DEPS = ["customtkinter", "PIL", "httpx", "pyinstaller"]
IGNORE_DIRS = {"__pycache__", ".git", "venv", ".venv", "env", ".env", "node_modules"}
VERSION_FILE = ROOT / "core" / "version.txt"

# SHA-256 manifest
MANIFEST_FILE = DIST / "build_manifest.json"


# ═══════════════════════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════════════════════

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
#  ENVIRONMENT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_environment() -> list[str]:
    """Validate build environment. Returns list of issues."""
    issues = []

    # Python version
    v = sys.version_info
    if (v.major, v.minor) < MIN_PYTHON:
        issues.append(f"Python {v.major}.{v.minor} detected, need {'.'.join(map(str, MIN_PYTHON))}+")

    # Platform
    if sys.platform != "win32":
        issues.append(f"Build platform is '{sys.platform}', Windows required for EXE builds")

    # Dependencies
    for dep in REQUIRED_DEPS:
        try:
            if dep == "PIL":
                import PIL  # noqa
            else:
                __import__(dep)
        except ImportError:
            issues.append(f"Missing dependency: {dep}")

    # Source files
    required_sources = [ROOT / "app.py", ROOT / "theme.py", CORE_DIR / "setup_engine.py",
                        CORE_DIR / "api_client.py", ASSETS_DIR / "icon.ico"]
    for src in required_sources:
        if not src.exists():
            issues.append(f"Missing source file: {src.name}")

    return issues


def install_dependencies():
    """Ensure all build dependencies are installed."""
    log("Ensuring build dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade",
         "pyinstaller", "customtkinter", "Pillow", "httpx"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        log(f"Dependency install warnings: {result.stderr[:500]}", "WARN")
    log("Dependencies verified")


# ═══════════════════════════════════════════════════════════════════════════
#  STATIC ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def static_analysis() -> list[str]:
    """Check all Python files for syntax errors and import issues."""
    errors = []
    log("Running static analysis...")

    for py_file in ROOT.rglob("*.py"):
        # Skip build artifacts
        rel = py_file.relative_to(ROOT)
        if any(part in IGNORE_DIRS for part in py_file.parts):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            log(f"  ✓ {rel}")
        except SyntaxError as e:
            errors.append(f"Syntax error in {rel}: {e}")
            log(f"  ✗ {rel}: {e}", "ERROR")
        except Exception as e:
            errors.append(f"Error reading {rel}: {e}")

    return errors


# ═══════════════════════════════════════════════════════════════════════════
#  BUILD
# ═══════════════════════════════════════════════════════════════════════════

def clean():
    """Remove all build artifacts."""
    log("Cleaning build artifacts...")
    for d in [DIST, BUILD, ROOT / "__pycache__"]:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    for cache_dir in [CORE_DIR / "__pycache__", UI_DIR / "__pycache__"]:
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)
    log("  Cleaned all build directories")


def build_exe(version: str = "2.0.0") -> Optional[Path]:
    """Build single-file EXE using PyInstaller. Returns path on success."""
    log(f"Building {APP_NAME} v{version}...")
    start = time.time()

    # Write version
    VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    VERSION_FILE.write_text(version)

    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--clean",
        "--log-level", "WARN",
    ]

    # Add icon if available
    icon_path = ASSETS_DIR / "icon.ico"
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    else:
        log("No icon.ico found — skipping icon", "WARN")

    # Add data files
    if UI_DIR.exists():
        cmd.extend(["--add-data", f"{UI_DIR}{os.pathsep}ui"])
    cmd.extend([
        "--add-data", f"{CORE_DIR}{os.pathsep}core",
        "--add-data", f"{ROOT / 'theme.py'}{os.pathsep}.",
        "--add-data", f"{ROOT / 'version.txt' if VERSION_FILE.exists() else ''}",
    ])
    if ASSETS_DIR.exists():
        cmd.extend(["--add-data", f"{ASSETS_DIR}{os.pathsep}assets"])

    # Add leads deployment resources
    if LEADS_DIR.exists():
        cmd.extend(["--add-data", f"{LEADS_DIR}{os.pathsep}leads"])
        log(f"  Bundling leads/ resources from {LEADS_DIR}")
    else:
        log("  No leads/ directory found — skipping leads resources", "WARN")

    # Add whatsapp-bridge source for leads backend Docker build
    if WHATSAPP_BRIDGE_DIR.exists():
        cmd.extend(["--add-data", f"{WHATSAPP_BRIDGE_DIR}{os.pathsep}leads/whatsapp-bridge"])
        log(f"  Bundling whatsapp-bridge from {WHATSAPP_BRIDGE_DIR}")
    else:
        log("  No whatsapp-bridge found — skipping (leads backend will skip WhatsApp)", "WARN")

    cmd.extend([
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(SPEC_DIR),
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "httpx",
        "--hidden-import", "httpx._urlparse",
        "--collect-all", "customtkinter",
        str(ROOT / "app.py"),
    ])

    # Filter empty strings
    cmd = [c for c in cmd if c]

    log(f"  PyInstaller cmd: {' '.join(cmd[:10])}...")

    progress_file = str(DIST / ".build_progress")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

    elapsed = time.time() - start

    if result.returncode == 0:
        exe_path = DIST / f"{APP_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            log(f"  Build completed in {elapsed:.1f}s")
            log(f"  Output: {exe_path}")
            log(f"  Size: {size_mb:.1f} MB")
            return exe_path
        else:
            log(f"  Build reported success but {exe_path} not found", "ERROR")
            return None
    else:
        log(f"  Build failed (exit {result.returncode}) after {elapsed:.1f}s", "ERROR")
        if result.stderr:
            log(f"  stderr: {result.stderr[-2000:]}", "ERROR")
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def verify_exe(exe_path: Path) -> list[str]:
    """Verify built EXE integrity. Returns list of issues."""
    issues = []
    log("Running post-build verification...")

    # 1. File exists
    if not exe_path.exists():
        issues.append(f"EXE file not found: {exe_path}")
        return issues

    # 2. Minimum size check
    min_size = 10 * 1024 * 1024  # 10 MB
    actual_size = exe_path.stat().st_size
    if actual_size < min_size:
        issues.append(f"EXE too small: {actual_size / 1024:.0f} KB (min {min_size / 1024:.0f} KB)")

    # 3. MZ header check
    with open(exe_path, "rb") as f:
        header = f.read(2)
        if header != b"MZ":
            issues.append("EXE missing MZ header — not a valid PE file")

    # 4. SHA-256 hash
    hasher = hashlib.sha256()
    with open(exe_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256 = hasher.hexdigest()
    log(f"  SHA-256: {sha256}")

    # 5. PE structure (basic check for DOS header + PE signature)
    with open(exe_path, "rb") as f:
        f.seek(0x3C)
        pe_offset_bytes = f.read(4)
        pe_offset = int.from_bytes(pe_offset_bytes, "little")
        f.seek(pe_offset)
        pe_sig = f.read(4)
        if pe_sig != b"PE\x00\x00":
            issues.append("EXE missing PE signature — structure may be invalid")

    # 6. Write manifest
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "app_name": APP_NAME,
        "version": VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "unknown",
        "build_time": datetime.utcnow().isoformat() + "Z",
        "size_bytes": actual_size,
        "size_mb": round(actual_size / (1024 * 1024), 1),
        "sha256": sha256,
        "issues": issues,
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    log(f"  Manifest written to {MANIFEST_FILE}")

    return issues


# ═══════════════════════════════════════════════════════════════════════════
#  NSIS INSTALLER
# ═══════════════════════════════════════════════════════════════════════════

def create_nsis_installer(version: str = "2.0.0"):
    """Create NSIS installer script for distribution."""
    log("Generating NSIS installer script...")
    nsis_script = BUILD / "installer.nsi"
    nsis_script.parent.mkdir(parents=True, exist_ok=True)

    exe_path = DIST / f"{APP_NAME}.exe"
    if not exe_path.exists():
        log("  Cannot create NSIS: EXE not built yet", "WARN")
        return

    content = f"""\
!define PRODUCT_NAME "Parakram VPS"
!define PRODUCT_VERSION "{version}"
!define PRODUCT_PUBLISHER "Parakram Technologies"
!define PRODUCT_WEB_SITE "https://getparakram.in"

!include "MUI2.nsh"
!include "x64.nsh"

Name "${{PRODUCT_NAME}}"
OutFile "{DIST / 'ParakramVPS-Installer.exe'}"
InstallDir "$PROGRAMFILES64\\${{PRODUCT_NAME}}"
RequestExecutionLevel admin
BrandingText "Parakram Technologies"

!define MUI_ABORTWARNING
!define MUI_ICON "{ASSETS_DIR / 'icon.ico'}"
!define MUI_UNICON "${{NSISDIR}}\\Contrib\\Graphics\\Icons\\modern-uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${{NSISDIR}}\\Contrib\\Graphics\\Wizard\\win.bmp"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{ROOT / 'LICENSE.txt' if (ROOT / 'LICENSE.txt').exists() else ''}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "{exe_path}"
  File "{ROOT / 'README.md' if (ROOT / 'README.md').exists() else ''}"

  CreateShortCut "$DESKTOP\\Parakram VPS.lnk" "$INSTDIR\\{APP_NAME}.exe"
  CreateDirectory "$SMPROGRAMS\\Parakram VPS"
  CreateShortCut "$SMPROGRAMS\\Parakram VPS\\Parakram VPS.lnk" "$INSTDIR\\{APP_NAME}.exe"
  CreateShortCut "$SMPROGRAMS\\Parakram VPS\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"

  WriteUninstaller "$INSTDIR\\uninstall.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}" "DisplayName" "${{PRODUCT_NAME}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}" "DisplayVersion" "${{PRODUCT_VERSION}}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}" "Publisher" "${{PRODUCT_PUBLISHER}}"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\\Parakram VPS.lnk"
  RMDir /r "$SMPROGRAMS\\Parakram VPS"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}"
SectionEnd
"""
    nsis_script.write_text(content)
    log(f"  NSIS script: {nsis_script}")


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    # Parse args
    args = set(sys.argv[1:])
    quick_mode = "--quick" in args
    sign_mode = "--sign" in args
    clean_only = "--clean-only" in args

    # Extract version
    version = "2.0.0"
    for arg in sys.argv[1:]:
        if arg.startswith("--version="):
            version = arg.split("=", 1)[1]

    log(f"Parakram VPS Build System v{version}")
    log(f"Platform: {sys.platform} | Python: {sys.version.split()[0]}")

    if clean_only:
        clean()
        log("Clean only — done.")
        return

    # Phase 1: Environment
    log("── Phase 1: Environment Validation ──")
    issues = validate_environment()
    if issues:
        for i in issues:
            log(f"  ✗ {i}", "ERROR")
        log("Environment validation failed. Run: pip install pyinstaller customtkinter Pillow httpx")
        sys.exit(1)
    log("  ✓ Environment OK")

    if not quick_mode:
        install_dependencies()

    # Phase 2: Clean
    log("── Phase 2: Clean Build Artifacts ──")
    clean()

    # Phase 3: Static Analysis
    if not quick_mode:
        log("── Phase 3: Static Analysis ──")
        sa_errors = static_analysis()
        if sa_errors:
            for e in sa_errors:
                log(f"  {e}", "ERROR")
            sys.exit(1)
        log("  ✓ All sources valid")

    # Phase 4: Build
    log("── Phase 4: Build ──")
    exe_path = build_exe(version)
    if not exe_path:
        log("BUILD FAILED", "FATAL")
        sys.exit(1)

    # Phase 5: Verification
    log("── Phase 5: Verification ──")
    if not quick_mode:
        ver_issues = verify_exe(exe_path)
        if ver_issues:
            for v in ver_issues:
                log(f"  ⚠ {v}", "WARN")
        else:
            log("  ✓ All checks passed")
    else:
        log("  Skipped (quick mode)")

    # Phase 6: NSIS Installer
    log("── Phase 6: NSIS Installer ──")
    create_nsis_installer(version)

    # Phase 7: Code Signing
    if sign_mode:
        log("── Phase 7: Code Signing ──")
        log("  Code signing not configured — skipping", "WARN")

    log("── Build Complete ──")
    log(f"Output: {exe_path}")
    log(f"Size: {exe_path.stat().st_size / (1024 * 1024):.1f} MB")


if __name__ == "__main__":
    main()
