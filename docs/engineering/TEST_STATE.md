# Test State

## Historical Green Runs
- Phase 2 Task 2.4: run 35610034968 — PASS on Python 3.11/3.12.
- Phase 3: run 35610333398 — PASS on Python 3.11/3.12.
- Phase 4-10: run 35611024600 — PASS on Python 3.11/3.12.
- Phase 11-20: run 35613550835 — PASS on Python 3.11/3.12.

## Current Sweep
New focused tests cover:
- CoreServices composition and durable domain state
- OCR benchmark measurement
- adversarial/failure handling
- Persian RTL/English UX validation and bounded pagination
- release audit evidence semantics

## Required Before Final Release
- full CI green
- Alembic upgrade/downgrade smoke test
- application startup/shutdown without Telegram credentials in safe test mode
- Telegram integration with real test account
- provider integration tests
- worker transport/recovery tests
- OCR benchmark against labeled real images
- backup/restore round-trip
- deployment/restart/rollback
- performance/load evidence
- security/dependency audit
