# Engineering Changelog

## 2026-09-21 — Phases 11-25 integration/hardening
- Composed Phase 11-20 services into CoreServices.
- Added durable domain-state and security-audit persistence models.
- Added Alembic initial and Phase 11-20 migrations.
- Added Phase 21 OCR benchmark metrics.
- Added Phase 22 adversarial/failure harness.
- Added Phase 23 Persian/English UX validation and bounded pagination.
- Added Phase 24 production evidence tracking.
- Added Phase 25 final release audit.
- Added focused tests.
- CI run 35614933655 passed on Python 3.11 and 3.12.
- PR #11 merged as a verified implementation unit.

## Final Gate
Only environment-dependent verification remains before final release: real Telegram/providers/worker/OCR dataset/deployment/performance/backup/recovery/security evidence.

## 2026-09-25 — GitHub Actions Runtime
- Added shared bot process entrypoint.
- Added manual Windows GitHub Actions runtime workflow with migrations and secure environment injection.
- Added Telegram StringSession support.
- Reviewed `siasoltoon/vps`; copied the Windows-runner deployment pattern only, excluding hardcoded credentials and insecure RDP configuration.
- CI 36177272784 passed on Python 3.11/3.12.

## 2026-09-25 — Multi-user Telegram onboarding
- Added persistent encrypted Telegram account records and migration 0003.
- Added phone/code/2FA authentication service with transient credentials.
- Added onboarding bot commands: /start, /connect, /status, /disconnect.
- Added independent linked-account runtime and per-account command routing.
- Added cryptography dependency and GitHub Actions secret configuration.
- CI 36179020202 passed on Python 3.11/3.12.

## 2026-09-25 — Telegram authentication code expiry recovery
- Diagnosed real runtime failure as `PhoneCodeExpiredError` during `sign_in`, despite a successful code request.
- Added Telegram code delivery metadata and elapsed-attempt diagnostics without logging code/hash secrets.
- Added explicit /resend recovery using a transient client and refreshed phone-code state.
- Preserved the code-entry state for recoverable expiry/invalid-code errors.
- Added regression coverage; PR #16 CI run 36184453774 passed on Python 3.11/3.12.
- Real Telegram retry remains environment-dependent and is not marked PASS.

## 2026-09-25 — Telegram authentication diagnostics
- Added structured authentication lifecycle/error logging for phone-code and 2FA stages.
- Added secure exception sanitization and identifier masking/fingerprinting.
- Added regression coverage ensuring authentication secrets do not appear in diagnostics.
- PR #15 CI run 36182724874 passed on Python 3.11 and 3.12.

## 2026-09-25 — Telegram resend protocol correction
- Real testing reproduced `PhoneCodeExpiredError` even after the fresh-client /resend flow.
- Verified that a true resend preserves the existing `phone_code_hash`; Telethon's `send_code_request()` uses `auth.resendCode` when its internal hash is present.
- Corrected /resend to reuse the existing transient Telethon client.
- Updated regression coverage to verify the same client handles the initial request, resend, and verification.
- PR #17 CI run 36185340785 passed on Python 3.11 and 3.12.

## 2026-09-25 — QR-first Telegram onboarding
- Replaced the production onboarding bot's phone/code chat interaction with Telethon QR login.
- Added in-memory QR PNG generation and short-lived challenge lifecycle management.
- Added background QR waiting, optional 2FA continuation, encrypted StringSession persistence, cancellation and cleanup.
- QR challenge media is removed from the onboarding chat after completion/expiry/failure; QR URLs/tokens are not logged.
- Added `qrcode[pil]` and QR lifecycle regression tests.
- PR #18 CI run 36186445250 passed on Python 3.11 and 3.12.
- Real Telegram QR onboarding reached Telegram acceptance and 2FA in the first external test, but the transient session expired before password completion; this was diagnosed as a lifecycle bug rather than an authentication-password failure.

## 2026-09-25 — QR post-scan 2FA lifetime fix
- PR #19 extends the pending transient authentication deadline when Telegram accepts the QR and raises `SessionPasswordNeededError`.
- Added regression coverage using a 1-second QR TTL and 5-second service TTL to prove cleanup cannot use the expired QR deadline during 2FA.
- PR #19 CI run 36187266466 passed on Python 3.11 and 3.12.
- PR #19 merged to `main` as `76a4e9d2887f1bebfee9eb0c5b5c5f5486294787`.
- Fresh real QR+2FA onboarding is now the next operator verification step.

## 2026-09-25 — QR session persistence and post-auth safety
- PR #20 corrected the transient production client from Telethon `MemorySession` to `StringSession`, preventing `session.save()` from returning `None` after successful QR/2FA authentication.
- Real runtime evidence showed Telegram had accepted the login and emitted a new-session security notification; the application then failed during durable session persistence. This was not a 2FA password rejection.
- PR #20 CI run 36187991097 passed and merged to `main` as `1a74d35d44f958466f9d16eab903253fbbf96fc0`.
- PR #21 added post-auth session revocation on durable persistence failure, explicit retryable persistence errors, and distinct invalid-2FA/persistence user messaging.
- PR #21 first CI run 36188334722 failed due to a regression-test expectation mismatch; corrected test then passed in CI run 36188868237 on Python 3.11/3.12.
- PR #21 merged to `main` as `df5b27344bcc498d252c4e5786119ca0702fa1fc`.
- Fresh real QR+2FA onboarding against current `main` is now the next operator verification step.
