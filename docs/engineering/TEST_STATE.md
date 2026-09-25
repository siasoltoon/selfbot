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

## Real Telegram External Verification — 2026-09-25
- Fresh real `/connect` against current main created and delivered a QR challenge.
- Telegram accepted the QR and requested 2FA; 2FA completed successfully.
- Application returned `اتصال با موفقیت انجام شد. شناسه داخلی تلگرام: 1261331908`.
- No post-auth persistence exception appeared in the runtime log; the client disconnected cleanly after finalization.
- RESULT: PASS for real QR + 2FA onboarding and application-level session finalization.

## Remaining External Verification
- `/status` active-account check
- linked-account message/command routing
- session reuse after controlled restart
- Alembic migration smoke test against real target database
- AI/STT/TTS/search providers
- PC Worker transport/heartbeat/claim/retry/offline recovery
- labeled OCR dataset benchmark
- backup/restore round trip
- deployment startup/health/restart/rollback
- performance/load evidence
- final security/dependency audit

A phase remains non-final until its required evidence is recorded.

## Global Capability Panel — 2026-09-25
- PR #23 final feature head c74a5a8194931a24807d35da19375346a92d610c: PASS.
- Python 3.11: compileall + pytest PASS.
- Python 3.12: compileall + pytest PASS.
- Regression tests added: tests/test_capability_panel.py and tests/test_runtime_panel.py.
- Coverage includes durable per-owner capability settings, authenticated compact panel tokens, outgoing /پنل routing from multiple chat types, and incoming-command rejection.
- Real Telegram Inline Mode/button interaction is NOT yet claimed PASS; it requires operator-side BotFather configuration and runtime verification.


## 2026-09-25 — Panel routing regression
- PR #24 CI run `36195321075` passed on Python 3.11 and 3.12.
- Real Telegram panel interaction is still pending after deployment of merge `71ed0106956e1e4d46fa47af9b2949c3e587b703`.
- Do not mark the runtime interaction as PASS until the current runtime is restarted and `/panel` is exercised in Saved Messages and onboarding-bot chat.
