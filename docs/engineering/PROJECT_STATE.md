# Project State

## Current Position
- Roadmap: Phases 1-25 code-side implementation/hardening sweep completed.
- Status: IN PROGRESS — final external verification gate. Real Telegram QR + 2FA onboarding has now succeeded on the current main runtime, including successful account identification after the previously fixed persistence failures.
- Latest implementation units: PR #20 fixed persistent `StringSession` creation and merged to `main`; PR #21 hardened post-auth persistence failure cleanup and merged to `main`.
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
- Secure structured diagnostics for Telegram authentication failures.
- QR onboarding with transient QR image delivery, background wait, QR expiry/cancellation cleanup, post-scan 2FA continuation, encrypted session persistence, and post-auth cleanup safety.

## Final External Verification Gate
The repository does not claim production release merely from framework/unit/CI evidence. Remaining work requires real provider behavior, labeled OCR data, real worker transport, deployed environments, backup/restore, performance/load and rollback/recovery evidence.

## Latest Runtime Integration
- Deployment-agnostic `scripts/run_bot.py` entrypoint is implemented.
- Manual GitHub Actions Windows runtime workflow applies migrations and starts the bot process.
- Temporary GitHub Actions SQLite remains a test/runtime environment only; PostgreSQL is the intended durable production store.
- Telegram StringSession encryption is configured through deployment-provided secrets.

## Multi-user Telegram Runtime
- Installation bot is separate from linked Telethon user-account sessions.
- Connected accounts run as independent Telethon clients and route commands per linked account.
- Persistent session records use encrypted storage and support revoke/disconnect.
- PR #15 added secure lifecycle/error diagnostics.
- PR #16/#17 hardened legacy code-expiry recovery; production onboarding uses QR.
- PR #18 introduced QR onboarding.
- PR #19 fixed post-scan 2FA lifetime.
- PR #20 fixed persistent StringSession serialization.
- PR #21 revokes an authenticated Telegram session if durable persistence fails.

## Real Telegram Verification — 2026-09-25
- A fresh real `/connect` run against current main successfully created a QR challenge.
- The QR was scanned and Telegram accepted it.
- Telegram requested 2FA and the 2FA step completed successfully.
- The application returned: `اتصال با موفقیت انجام شد. شناسه داخلی تلگرام: 1261331908`.
- Runtime logs show no persistence exception after 2FA; the authenticated client disconnected cleanly afterward.
- This is PASS evidence for real QR + 2FA onboarding and application-level session finalization.

## Next
1. Verify `/status` reports the connected account as active.
2. Verify linked-account message/command routing with the connected account.
3. Verify session reuse after a controlled application restart without repeating QR authentication.
4. Continue the broader external verification matrix: real database, providers, worker, OCR, backup/restore, deployment, performance and security.
Do not mark the entire project release PASS until those evidence items are completed.

## 2026-09-25 — Global Telegram Capability Panel
- PR #23 merged to main as 68203f444ceae87159ecee813908c683297039ff.
- Added durable owner-scoped capability state backed by the existing domain_state store.
- Added the full master-spec capability registry: AI, long-term memory, voice, web intelligence, plugins, PC Worker, automation, reminders, backup/restore, analytics, controlled learning, multi-agent AI, OCR, plus always-on tasks/scheduler and security.
- Added /panel and /پنل handling for outgoing linked-account commands.
- Panel requests can originate from Saved Messages, private chats and groups; the linked user account invokes the onboarding bot through Telegram Inline Mode so interactive controls can be inserted into the same chat.
- Added signed panel tokens, callback sender verification and owner-scoped durable toggles.
- Added /capability <id> on|off as a text fallback/control path.
- CI for the final feature head c74a5a8194931a24807d35da19375346a92d610c passed on Python 3.11 and 3.12.
- One-time operator setup remains: enable Inline Mode for the onboarding bot with BotFather /setinline.
- Capability enabled state is distinct from external provider/worker availability; unavailable dependencies must still fail safely.
