# Project State

## Current Position
- Roadmap: Phases 1-25 code-side implementation/hardening sweep completed.
- Status: IN PROGRESS — final external verification gate; Telegram resend protocol hardening is implemented pending CI and real Telegram verification.
- Latest merged implementation: PR #14, merge commit bb5cf7f70e5d48f6158eaa24da728e3000e53eae.
- Latest merged implementation: PR #16, Telegram login code-expiry recovery.
- New hardening branch: Telegram resend protocol now reuses the same Telethon client so `send_code_request()` can follow Telethon's `auth.resendCode` path.

## Completed Code-Side Work
- Phases 0-3 foundation/plugin system.
- Phases 4-10 core capability boundaries.
- Phases 11-20 capability services, composition, durable domain-state boundary and migrations.
- Phase 21 OCR benchmark framework.
- Phase 22 adversarial/failure harness.
- Phase 23 Persian/English UX validation and bounded pagination.
- Phase 24 production-hardening evidence model.
- Phase 25 final-release audit model.
- Multi-user Telegram onboarding with encrypted Telethon StringSession persistence.
- Secure structured diagnostics for Telegram phone-code and 2FA authentication failures.

## Final External Verification Gate
The repository does not claim production release merely from framework/unit/CI evidence. Remaining work requires real credentials, real Telegram/provider behavior, labeled OCR data, real worker transport, deployed environments, backup/restore, performance/load and rollback/recovery evidence.

## Latest Runtime Integration
- Added deployment-agnostic `scripts/run_bot.py` entrypoint.
- Added manual GitHub Actions Windows runtime workflow.
- Workflow applies Alembic migrations and starts the bot process on every manual run.
- Inspected `siasoltoon/vps`: retained its Windows-runner pattern, but did not copy hardcoded credentials or unsafe RDP authentication settings.
- Telegram StringSession secrets are now supported explicitly.

## Multi-user Telegram Runtime
- Multi-user onboarding implementation added in PR #14: phone → Telegram code → optional 2FA → encrypted Telethon session.
- Normal BotFather onboarding bot is separate from linked user-account sessions.
- Persistent session records use encrypted storage and support revoke/disconnect.
- Connected accounts run as independent Telethon clients and route commands per linked account.
- PR #15 adds lifecycle/error diagnostics while redacting login codes, passwords, phone_code_hash, API credentials, and session material.
- PR #16 adds recoverable code-expiry handling and `/resend`; follow-up hardening corrects `/resend` to reuse the existing client/auth hash instead of starting a separate authorization request.

## Next
Run targeted CI for the resend-protocol fix, then repeat the real Telegram `/connect` flow. If the code expires, use `/resend` once and enter only the newly delivered code. Record the exact external result before advancing the final verification matrix.
