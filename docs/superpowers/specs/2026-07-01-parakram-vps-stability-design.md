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
- **✅ DELIVERED**: Packaging migrated from PyInstaller EXE (AV false-positive prone) → WiX v7 MSI
- **✅ DELIVERED**: Dashboard replaced from PowerShell HttpListener → React 19 + Vite + Express 5 (TypeScript)
- **✅ DELIVERED**: CI smoke test: `vps-release.yml` runs silent MSI install → verifies service + dashboard → uninstall on `windows-latest` runner
- **✅ DELIVERED**: Code-signing in CI pipeline (self-signed cert via `VPS_CODESIGN_PFX_BASE64` + `VPS_CODESIGN_PASSWORD` secrets, gracefully skipped if absent)
- **✅ DELIVERED**: Multi-component WiX generation (frontend + asset directories, correct MIME types)
- Old Python installer (`windows-vps/installer/`) is dead code as of v3 — kept as reference for porting Caddy/Nebula/restic/Leads hosting
- Dashboard also lists Caddy, Nebula, restic, Leads (not yet provisioned by v3 MSI)

## Root Cause Analysis
The recurring pattern — bugs only surfacing after a release build on a real Windows machine — implied **no clean-VM smoke test existed in CI**. This gap is now closed: `vps-release.yml` includes a full install→verify→uninstall smoke test on `windows-latest`.

## Target Architecture
Three concrete workstreams — status:

1. **✅ CI clean-install verification**: DONE — `vps-release.yml` builds MSI, installs silently, curls `localhost:9876`, verifies service, uninstalls.
2. **⏳ Checkpoint system audit**: DEFERRED — the old Python installer (`setup_engine.py`) is dead code in v3. Re-audit when porting its steps to `provision.ps1`.
3. **⏳ Auto-update path**: DEFERRED — the v3 dashboard `/a/update-check` endpoint is still a stub (`{available: false}`). Implement when adding real update logic to the Node backend.

## Error Handling
- Every checkpoint step must log a structured, human-readable failure reason to a local log file the dashboard can surface — no more silent `KeyError`-style crashes.
- Installer must validate all required inputs (tunnel name, optional Cloudflare token) before starting irreversible steps.

## Testing
- New: CI clean-VM install smoke test (highest priority — see above)
- New: idempotency test per checkpoint step (can run steps twice, assert no duplicate services/no corruption)
- New: updater round-trip test
- Existing 20 test files kept as-is unless touched during fixes

## Task List

### ✅ Delivered
1. ✅ MSI packaging (WiX v7) — replaces PyInstaller EXE (AV false-positive solved)
2. ✅ CI clean-VM install smoke test — `vps-release.yml` runs on `windows-latest`
3. ✅ Code-signing pipeline (self-signed, graceful fallback)
4. ✅ React 19 + Vite + Express 5 dashboard (replaces PowerShell HttpListener)
5. ✅ Multi-component WiX generation (frontend + assets correctly routed)
6. ✅ Verified: fresh MSI installs, service runs, dashboard renders with live data

### 🔜 Pending (deferred to future v3.x releases)
1. Port Caddy, Nebula, restic, Leads-backend-hosting from old Python `setup_engine.py` → `provision.ps1`
2. Implement auto-update in dashboard backend (`/a/update-check` is currently a stub)
3. Cloudflare Tunnel token UI in dashboard
4. Replace self-signed cert with Azure Trusted Signing or OV cert

## Open Risks
- Antivirus false-positives can reappear even with MSI if Windows Defender heuristics change — consider code-signing the MSI if a certificate becomes available (out of scope for now, note as future work)
- Docker-Compose-based Leads hosting inside the installer adds real complexity/fragility — if the clean-VM test reveals this is the main source of breakage, consider making it a clearly-labeled "advanced/optional" step rather than part of the default path
