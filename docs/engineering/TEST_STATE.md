# Test State

## Historical Green Runs
- Phase 2 Task 2.4: 35610034968 — PASS on Python 3.11/3.12.
- Phase 3: 35610333398 — PASS on Python 3.11/3.12.
- Phase 4-10: 35611024600 — PASS on Python 3.11/3.12.
- Phase 11-20: 35613550835 — PASS on Python 3.11/3.12.
- Phases 11-25 integration/hardening: 35614933655 — PASS on Python 3.11/3.12.
- Runtime integration: 36177272784 — PASS on Python 3.11/3.12.
- Multi-user Telegram onboarding: 36179020202 — PASS on Python 3.11/3.12.
- PR #14 merge verification: 36179129789 — PASS on Python 3.11/3.12.

## Latest Verification
- PR #15 CI run 36182724874 — PASS on Python 3.11 and 3.12.
- Both compile and pytest steps completed successfully.
- New regression test covers safe Telegram authentication error diagnostics.

## Telegram Expiry Recovery Verification
- PR #16 CI run 36184453774 — PASS on Python 3.11 and 3.12.
- Coverage includes fresh-client resend after `PhoneCodeExpiredError`, pending-state preservation, code-attempt lifecycle metadata, and safe recovery cleanup.
- Real Telegram resend/login remains environment-dependent and is not marked PASS.
- PR #17 CI run 36185340785 — PASS on Python 3.11 and 3.12; both compile and pytest steps completed successfully.
- PR #18 CI run 36186445250 — PASS on Python 3.11 and 3.12; compile and pytest completed successfully.
- PR #18 adds QR lifecycle tests for PNG generation, successful persistence, 2FA continuation, and cancellation/cleanup.
- Real Telegram QR onboarding remains NOT PASS until operator evidence is recorded.

## Remaining External Verification
- Real Telegram login/session and message flow
- Alembic migration smoke test against real target database
- AI/STT/TTS/search providers
- PC Worker transport/heartbeat/claim/retry/offline recovery
- labeled OCR dataset benchmark
- backup/restore round trip
- deployment startup/health/restart/rollback
- performance/load evidence
- final security/dependency audit

A phase remains non-final until its required evidence is recorded.
