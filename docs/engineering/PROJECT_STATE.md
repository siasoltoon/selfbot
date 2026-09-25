# Project State

## Current Position
- Roadmap: Phases 1-25 code-side implementation/hardening sweep completed.
- Status: IN PROGRESS — final external verification gate; Telegram QR+2FA lifecycle is now CI-verified and the next required step is a fresh real Telegram QR onboarding test.
- Latest implementation unit: PR #19, QR post-scan 2FA lifetime fix, merged to `main` as `76a4e9d2887f1bebfee9eb0c5b5c5f5486294787`.
- Production onboarding uses QR login as the primary flow, with transient 2FA support; phone/code chat login is not the production interaction.

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
- QR onboarding with transient QR image delivery, background wait, QR expiry/cancellation cleanup, post-scan 2FA continuation, and encrypted session persistence.
- PR #19 fixes the lifecycle bug where the original short QR expiry could disconnect the transient client before 2FA verification.

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
- PR #16 adds recoverable code-expiry handling and /resend; PR #17 corrected the resend protocol. PR #18 moves the production onboarding interaction to QR login.
- PR #19 extends the transient client lifetime after Telegram accepts the QR and requests 2FA, preventing cleanup from using the original QR TTL during password entry.

## Next
Run the real Telegram /connect flow against current `main`. Scan the QR with another already-authorized Telegram device, complete 2FA if requested, and verify encrypted session persistence plus linked-account message routing. Do not mark the flow PASS until this external evidence succeeds.
