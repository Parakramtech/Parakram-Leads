# Parakram VPS — Stability & Clean-Install Design

## Context
Parakram VPS (`windows-vps/`) turns a Windows machine into a self-hosted server (OpenSSH + Cloudflare Tunnel + dashboard + optional Leads backend hosting via Docker Compose). Git history shows a pattern of reactive firefighting: a silent `KeyError` crash on EXE startup, antivirus false-positives on the PyInstaller build (worked around by switching to WiX MSI), broken signup/signin API paths, and a UTF-8/cp1252 crash in the build script. Test coverage is ~17% (20 of ~115 Python files). This is a portfolio project — the goal is a genuinely reliable one-click installer, not real subscription revenue.

## Goal
On a **clean Windows 10/11 VM with nothing pre-installed**, running `ParakramVPS-Setup.msi` produces a working local dashboard (`http://localhost:9876`), a working SSH connection, and (optionally) a Cloudflare Tunnel URL — with zero manual intervention and zero antivirus quarantine — every time, not just on the developer's machine.

## Non-Goals
- Real Razorpay billing enforcement, real customer support flows
- The Edge Network marketplace (separate, later-stage idea)
- Linux installer parity work (lower priority than fixing the Windows path, which is the flagship)

## Current State (from exploration)
- Installer: `windows-vps/installer/app.py` (customtkinter GUI) → `core/setup_engine.py` (checkpointed installation steps) → `core/api_client.py`
- Packaging: PyInstaller → EXE (caused AV false positives) → migrated to WiX MSI (`windows-vps/wix/`)
- Dashboard: PowerShell HttpListener server generated as a raw string in `_generate_server_script()`, HTML in `_generate_dashboard_html()`
- Optional Leads backend hosting via Docker Compose bundled under `windows-vps/installer/leads/`
- Each of the 4 recent fix commits addressed a *symptom* found late (post-build), not a systemic gap in pre-release verification

## Root Cause Analysis (to do first, before more patches)
The recurring pattern — bugs only surfacing after a release build on a real Windows machine — implies **no clean-VM smoke test exists in CI**. Fixes have been reactive patches to individual crashes rather than closing that verification gap. The design below treats "add a clean-VM install test to CI" as the highest-leverage single change.

## Target Architecture
No rewrite. Three concrete workstreams:

1. **CI clean-install verification**: Add a CI job (GitHub Actions `windows-latest` runner, fresh each run) that builds the MSI and actually installs it silently (`msiexec /i ... /qn`), then curls `localhost:9876` and asserts a 200 response. This is the test that would have caught all four historical bugs before release.
2. **Checkpoint system audit**: Walk every step in `Checkpoint.STEPS` / `run_all()` in `setup_engine.py` and confirm each is truly idempotent (re-running after a failure at step N doesn't redo or corrupt steps 1..N-1), matching the documented design intent.
3. **Auto-update path test**: `core/updater.py` was flagged as "not heavily tested" — write a test that simulates an update from a prior version and confirms the dashboard/service survive it.

## Error Handling
- Every checkpoint step must log a structured, human-readable failure reason to a local log file the dashboard can surface — no more silent `KeyError`-style crashes.
- Installer must validate all required inputs (tunnel name, optional Cloudflare token) before starting irreversible steps.

## Testing
- New: CI clean-VM install smoke test (highest priority — see above)
- New: idempotency test per checkpoint step (can run steps twice, assert no duplicate services/no corruption)
- New: updater round-trip test
- Existing 20 test files kept as-is unless touched during fixes

## Task List (for later `writing-plans`)
1. Add clean-VM install CI job (windows-latest, silent MSI install, curl dashboard)
2. Run it once to see what still breaks on a truly clean machine (expect surprises)
3. Fix whatever the clean-VM job finds
4. Audit + fix checkpoint idempotency in `setup_engine.py`
5. Add updater round-trip test; fix `updater.py` gaps it finds
6. Re-run full manual install on a real clean VM as final human verification

## Open Risks
- Antivirus false-positives can reappear even with MSI if Windows Defender heuristics change — consider code-signing the MSI if a certificate becomes available (out of scope for now, note as future work)
- Docker-Compose-based Leads hosting inside the installer adds real complexity/fragility — if the clean-VM test reveals this is the main source of breakage, consider making it a clearly-labeled "advanced/optional" step rather than part of the default path
