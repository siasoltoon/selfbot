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


## 2026-09-26 Panel v2
- Telegram management panel upgraded to a hierarchical Control Center and merged as d504af985246efa1480b73182b17c790a56bc175.
- Main → category → module → sub-capability navigation is implemented with durable owner-scoped state.
- Real Telegram UI verification of the nested panel remains pending.
\n\n## 2026-09-26 — Internal Diamond Economy\n- PR #27 merged to main as 508472022e61577a1597d016012893b31a891c14.\n- Added persistent per-user DiamondWallet and append-only DiamondTransaction ledger.\n- Added atomic user-to-user transfer with self-transfer rejection, sufficient-balance validation, minimum/maximum transfer, daily transfer cap, and configurable fee.\n- Added owner-only admin credit/debit with bounded adjustment size, reason and ledger audit fields.\n- Added .موجودی, .انتقال, .تاریخچه and admin adjustment commands; username and reply recipients are resolved through the linked Telegram client.\n- Safe defaults: min 1, max 1,000, daily 3,000, fee 1% with min 1/max 100, admin adjustment max 100,000.\n- Added Alembic migration 0004 and environment overrides; no Myoi/external-bot balance is used.\n- CI for PR #27 passed on Python 3.11 and 3.12.\n- Economy code-side implementation is complete; real PostgreSQL/runtime Telegram transaction verification remains external evidence.\n

## 2026-09-26 — Real Panel Execution + Myoi Adapter
- PR #29 merged as 76bf9d32fcefc17f9cfa9bf42c09ff00a1e57822.
- Panel capability gates now execute real core behaviors for calculator, ping, status, date/time, ID and owner task cancellation; enabling a child capability also activates its parent module.
- PR #30 merged as 965b0e925c2bd832d8b8ac3cd966c396e80fbb4c.
- Added a real Telethon Myoi adapter for @MeowieeeQBot: bot resolution, command sending, recent-message/button observation and visible-label button clicking. It is exposed from linked-account runtime.
- Myoi-specific workflows are deliberately not guessed; real bot behavior must be observed before implementing fishing/factory/roulette/etc.


## 2026-09-27 — External Database Persistence
- `DATABASE_URL` now supports SQLite, PostgreSQL and SQL Server via `mssql+pyodbc`.
- Added durable migration `0003_durable_runtime_state` for domain state, security audit, encrypted Telegram sessions and internal diamond economy tables.
- Alembic metadata now imports every durable ORM model so fresh external databases receive the required schema.
- GitHub Windows runtime installs the optional SQL Server driver and performs a database ping after migrations.
- External SQL Server connectivity is configuration-dependent; no external database is claimed PASS until an operator provides a reachable database and runs the migration smoke test.


## 2026-09-30 — External SQL Server Verification COMPLETE
- Real operator-hosted SQL Server connectivity verified from the local project environment through SQLAlchemy + pyodbc using `mssql+pyodbc`.
- `python -m alembic upgrade head` completed successfully through `0004_diamond_economy`.
- SQL Server `dbo.alembic_version` reports `0004_diamond_economy`; all expected durable tables were observed.
- Encrypted Telegram session write/read/decrypt/cleanup smoke test passed against the real SQL Server database.
- Multi-user runtime reload smoke test passed: a new `MultiUserTelegramRuntime` reconstructed from the same durable store loaded the encrypted session twice, authorized the client, and stopped cleanly; cleanup passed.
- Full local pytest suite after PR #37 merge passed with no failures.
- PR #37 merged to `main` as `65594754cdfed7e2e0cd6006d55c5e464ebaa1d8`.
- External SQL Server persistence gate is now PASS. This does not imply the entire project release is PASS; remaining provider, worker, OCR, deployment, backup/recovery, performance and live Telegram routing evidence remains.


## 2026-10-01 — Telegram Panel SQL Connectivity Resilience
- Real runtime logs showed the panel failure path was blocked by transient SQL Server connectivity from the GitHub Actions runner to the operator PC over Tailscale; Inline Mode was confirmed active and panel code-side tests were already green.
- PR #42 (fix(db): harden runtime against transient SQL connectivity) merged to main as 750ed593ededda0c19ded9ac68dc76701c143689.
- Database sessions now retry only initial connection checkout with bounded exponential backoff; pooled network connections use pre-ping/recycle and SQL Server connection attempts have a bounded timeout. Application work is never replayed automatically.
- Retry settings are deployment-configurable through DATABASE_CONNECT_RETRIES and DATABASE_CONNECT_RETRY_DELAY.
- CI run 36839640139 passed on Python 3.11 and 3.12.
- This improves resilience to brief DB/Tailscale interruptions but does not prove the home-PC SQL endpoint is continuously reachable for the full GitHub runtime. Real Telegram panel interaction remains pending.


## 2026-10-01 — Runtime Migration Connectivity Resilience
- Runtime workflow run 36840274511 failed during Prepare database, before the Telegram bot started.
- Root cause was confirmed from the job log: Alembic created a one-shot SQLAlchemy connection to 100.114.8.105:1433 and received ODBC 18 error 08001 / TCP timeout 258.
- The previously merged PR #42 protected application ORM sessions but did not protect Alembic's separate migration connection path.
- PR #43 (fix(db): make runtime migrations resilient to transient SQL outages) merged as 02ac2504fb81792e969c636b2153808725e1ce37.
- Alembic now reuses the bounded pre-work connection retry helper, SQL Server migration connections use a 10-second driver timeout, and runtime retry settings are explicit in the workflow.
- PR #43 CI run 36840788999 passed on Python 3.11 and 3.12 after fixing a test-file formatting regression.
- No Telegram session, encryption key, SQL credential, firewall exposure, or Inline Mode configuration was changed.
- Real Telegram panel interaction is still NOT PASS because the failed run never reached Start Telegram bot.


## 2026-10-01 — Persisted Telegram Session Restore Fix
- Runtime 36841201279 passed Tailscale and Alembic migration, then failed during `Start Telegram bot` while restoring the encrypted durable Telegram session.
- Root cause: `MultiUserTelegramRuntime._new_client()` passed the decrypted StringSession payload directly to `TelegramClient`. Telethon interprets a plain string argument as a SQLite session filename, causing `sqlite3.OperationalError: unable to open database file` on the GitHub runner.
- PR #44 merged as `fd2cbf8c1e9a9b682b942a69546b585310624a7c`; CI 36841546134 passed.
- `_new_client()` now explicitly wraps persisted payloads with `telethon.sessions.StringSession`.
- No Telegram session or secrets were regenerated. The existing encrypted database record remains the source of truth.
- Next: fresh Telegram Bot Runtime from this main commit, then verify startup and real `/پنل` interaction.
