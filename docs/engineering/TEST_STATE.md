# Test State

## Historical Green Runs
- Phase 2 Task 2.4: 35610034968 — PASS on Python 3.11/3.12.
- Phase 3: 35610333398 — PASS on Python 3.11/3.12.
- Phase 4-10: 35611024600 — PASS on Python 3.11/3.12.
- Phase 11-20: 35613550835 — PASS on Python 3.11/3.12.
- Phases 11-25 integration/hardening: 35614933655 — PASS on Python 3.11/3.12.

## Verified Code-Side Coverage
- service composition and durable domain state
- migrations/schema definitions
- OCR benchmark metric calculation
- adversarial/failure harness
- Persian RTL/English UX validation and bounded pagination
- release evidence semantics

## Latest Verification\n- CI 36177272784 — PASS on Python 3.11/3.12 after runtime integration changes.\n\n## Latest Verification
- CI 36179020202 — PASS on Python 3.11/3.12 after multi-user Telegram onboarding implementation.
- Coverage includes encrypted session persistence, revoke flow, phone validation, 2FA branch, transient login cleanup, and linked-account routing.

## Remaining External Verification
- Alembic upgrade/downgrade smoke test against real target database
- Telegram login/session and message flow
- AI/STT/TTS/search providers
- PC Worker transport/heartbeat/claim/retry/offline recovery
- labeled OCR dataset benchmark
- backup/restore round trip
- deployment startup/health/restart/rollback
- performance/load evidence
- final security/dependency audit

A phase remains non-final until its required evidence is recorded.
