# Parakram Edge — Working Relay & End-to-End Demo Design

## Context
Parakram Edge (`Parakram-edge/`, separate repo) is an Android app (Kotlin/Compose/Ktor, modern stack) plus a Windows companion (Go, clean 7MB binary) that together let a desktop AI agent read phone sensors, files, and shell access over the local network or a cloud relay. Exploration found the Android app and Windows companion both genuinely functional (~70% complete), but the **Cloudflare Worker relay's entry point (`relay/src/index.ts`) is a literal empty file** — meaning the flagship "AI agent talks to your phone from anywhere over the internet" capability does not actually work yet, only the LAN path does. There's also a weak HMAC key derivation in `CameraStreamController.kt` and thin test coverage (4 files).

## Goal
A single scripted demo: pair an Android phone with the Windows companion (or directly with an agent) **over the internet, not just LAN** — e.g. Claude or another agent, running anywhere, reads a live sensor value (battery, GPS, or a camera-triggered QR read) from the phone via the Cloudflare relay. This is the single missing piece that turns Edge from "a local API on your phone" into "a pocket edge server for AI agents," which is the actual pitch in VISION.md.

## Non-Goals
- Plugin marketplace/registry monetization (Registry/Billing workers) — functional enough already, not the blocker
- Publishing SDKs to PyPI/npm — nice-to-have, not required for the demo
- iOS support, Raspberry Pi nodes, or any Edge Network marketplace scope

## Current State (from exploration)
- Android: Ktor server (port 8080), UTAP SQL-like interface, hardware/sensor endpoints, Room DB, Hilt DI, CameraX+ML Kit, HMAC-signed camera stream tokens, rate limiter (token bucket) — all functional
- Windows companion: Go binary, mDNS discovery, pairing handshake (QR → SHA256(challenge+pin) → `/api/auth/pair/secure-handshake` → `X-Agent-Key`), clipboard/file transfer — functional over LAN
- Cloud: `relay/src/index.ts` is empty (0 bytes); `relay-room.ts` (the actual Durable Object relay logic) exists and appears designed correctly, it's just never wired to a router
- Registry (plugin marketplace) and Billing (Razorpay) workers are separately functional but not part of this demo's critical path
- Security gaps found: HMAC key in `CameraStreamController.kt:60` derived from a repeated/truncated UUID string instead of `SecureRandom` — weak for anything beyond a demo, should still be fixed since it's cheap
- Tests: only 4 files, none covering UTAP endpoints, rate limiter, or camera token signing

## Target Architecture
1. **Wire the relay**: Implement `relay/src/index.ts` as the Cloudflare Worker HTTP entry point that handles the WebSocket upgrade request, extracts `deviceId`/`role`/`token`, and routes to the correct `RelayRoom` Durable Object instance (one DO per paired device-pair). This is pure wiring — the DO logic already exists in `relay-room.ts`.
2. **Auth token for relay**: Confirm/define how a device proves it's allowed to join a given `RelayRoom` (reuse the existing pairing `X-Agent-Key` scheme rather than inventing a new one).
3. **Fix HMAC key generation**: Replace the UUID-based derivation with `SecureRandom.nextBytes(32)` (or Android Keystore-backed key) in `CameraStreamController.kt`.
4. **Demo script**: a documented, repeatable sequence — phone app running → Windows companion (or a small Python/TS SDK script) connects via the relay URL → issues one read (e.g. GET battery state or trigger QR scan) → prints the result — provable end-to-end over two different networks (e.g. phone on mobile data, agent on a different Wi-Fi).

## Error Handling
- Relay must reject connections with invalid/expired pairing tokens with a clear error code, not a silent close
- If the Durable Object for a `deviceId` doesn't exist yet (device never paired), return a clear 404/error rather than creating an orphaned room

## Testing
- New: a test for the relay Worker routing (can be a lightweight Miniflare/Workers-vitest test) that confirms a WebSocket upgrade request with a valid token reaches the right DO
- New: unit test for the fixed HMAC key generation (confirms randomness/length, not a specific value)
- New: one test covering a UTAP endpoint's input sanitization (`sanitizeIdentifier`/`validateWhereClause`) — exploration flagged the blocklist approach as weaker than parameterized queries; test should at minimum confirm known SQL-injection patterns are rejected today, and flag if not
- Skip broad coverage push — 4 targeted tests covering the riskiest surfaces (relay auth, crypto, SQL sanitization) matter more than a number

## Task List (for later `writing-plans`)
1. Implement `relay/src/index.ts` request routing to `RelayRoom` DO
2. Deploy relay Worker to Cloudflare (needs Cloudflare account/API token — confirm access)
3. Fix `CameraStreamController.kt` HMAC key generation
4. Write the 3 targeted tests above
5. Build/document the end-to-end demo script (two-network proof)
6. Record or script a repeatable demo walkthrough for portfolio use

## Open Risks
- Deploying the relay Worker requires actual Cloudflare account access/credentials — confirm before starting this spec's implementation
- The UTAP blocklist-based SQL sanitization may need to become parameterized rather than just tested — if the new test reveals it's actually bypassable, that becomes a must-fix, not just a documented risk
