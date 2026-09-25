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
- Coverage includes recoverable expiry/invalid-code state handling and resend lifecycle.
- PR #17 CI run 36185340785 — PASS on Python 3.11 and 3.12; both compile and pytest steps completed successfully.
- Real Telegram code-in-chat onboarding was not accepted as production flow after repeated `PhoneCodeExpiredError`.

## QR Verification
- PR #18 CI run 36186445250 — PASS on Python 3.11 and 3.12; compile and pytest completed successfully.
- PR #18 adds QR lifecycle tests for PNG generation, successful persistence, 2FA continuation, and cancellation/cleanup.
- Real QR test reached Telegram acceptance and 2FA but failed before completion because the original QR TTL also governed the post-scan transient client lifetime.
- PR #19 CI run 36187266466 — PASS on Python 3.11 and 3.12; compile and pytest completed successfully.
- PR #19 regression test uses a 1-second QR TTL and 5-second service TTL, verifies the post-scan expiry is extended, and completes the simulated 2FA flow.
- PR #19 was merged to main as 76a4e9d2887f1bebfee9eb0c5b5c5f5486294787.
- Real Telegram QR+2FA onboarding remains NOT PASS until the operator reruns the external flow successfully.
- Real test interpretation: Telegram-side security notification indicated authentication succeeded; the application failure occurred during durable session persistence, not at 2FA validation.
- PR #20 CI run 36187991097 — PASS; verifies production QR client uses `StringSession` and persists the serialized session.
- PR #21 CI run 36188334722 — FAIL on the first attempt due to a test expectation mismatch; fixed. PR #21 CI run 36188868237 — PASS on Python 3.11/3.12; verifies authenticated-session revocation when persistence fails.

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
