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

## 2026-09-25 — Telegram authentication diagnostics
- Added structured authentication lifecycle/error logging for phone-code and 2FA stages.
- Added secure exception sanitization and identifier masking/fingerprinting.
- Added regression coverage ensuring authentication secrets do not appear in diagnostics.
- PR #15 CI run 36182724874 passed on Python 3.11 and 3.12.
- Next external step: repeat real Telegram `/connect` and use the sanitized diagnostic event to identify any remaining authentication failure.
