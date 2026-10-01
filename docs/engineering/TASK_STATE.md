# Task State

## Active Task
Complete real multi-user Telegram onboarding verification and prove session reuse/routing after successful QR + 2FA authentication.

## Status
IN PROGRESS — the first successful real QR + 2FA onboarding has now completed against the current main runtime. The application returned internal Telegram ID `1261331908` after QR approval and 2FA, with no post-auth persistence exception.

## Latest Verified Implementation
- PR #14 implements multi-user onboarding and independent account runtime.
- PR #18 adds Telethon QR login as the production onboarding path.
- PR #19 extends the pending session lifetime when QR authentication succeeds and Telegram requests 2FA.
- PR #20 changes production QR clients to persistent `StringSession`.
- PR #21 revokes authenticated sessions if durable persistence fails and distinguishes invalid 2FA from persistence failures.
- PR #21 CI run 36188868237 passed on Python 3.11/3.12.

## Real QR Verification — 2026-09-25
- QR generation and delivery succeeded.
- QR scan and Telegram-side acceptance succeeded.
- Telegram requested 2FA and the user completed the 2FA step.
- The application returned `اتصال با موفقیت انجام شد. شناسه داخلی تلگرام: 1261331908`.
- Runtime logs show the client disconnecting cleanly after successful completion.
- No `MemorySession`/None-session persistence error occurred.
- No persistence-failure cleanup path was triggered.

## Remaining Operator/Environment Work
1. Send `/status` from the onboarding bot and verify the newly connected account is shown as active.
2. Exercise one linked-account command/message path and verify routing uses the connected account.
3. Perform a controlled application restart while retaining the same durable database/session store, then verify the account reconnects without QR.
4. Verify the encrypted persisted session survives the restart and is not exposed in logs.
5. Continue broader external verification: real PostgreSQL, AI/STT/TTS/search providers, PC Worker transport/heartbeat/claim/retry/offline recovery, OCR dataset benchmark, backup/restore, deployment startup/restart/rollback, performance/load and final security/dependency audit.

## Rule
Do not fabricate PASS for environment-dependent checks. Any failure discovered there becomes a new targeted engineering task.

## Completed Task — Global Telegram Capability Panel
- Implemented and merged PR #23 as 68203f444ceae87159ecee813908c683297039ff.
- /panel and /پنل are recognized from outgoing linked-account messages.
- The same panel path supports Saved Messages, private chats and groups through the onboarding bot's Inline Mode.
- Capability state is durable and owner-scoped; callbacks are authenticated and owner-checked.
- The panel exposes the master-spec capability set and keeps security/tasks always enabled.
- /capability <id> on|off provides a text control fallback.
- CI c74a5a8194931a24807d35da19375346a92d610c passed on Python 3.11/3.12.

## Next Task
1. Enable Inline Mode for the onboarding bot via BotFather /setinline.
2. Restart the current runtime with the merged main commit.
3. Send /پنل in Saved Messages and verify the inline panel is inserted into Saved Messages.
4. Toggle at least one capability on and off and verify the message updates and state persists.
5. Repeat /پنل in a private chat and a group.
6. Verify an incoming group member cannot trigger capability control.
7. Continue session-reuse and broader production verification.



## 2026-09-25 — Panel command routing fix
- Root cause confirmed: the onboarding bot did not route `/panel` or `/پنل` at all; global linked-account routing existed, but bot-chat invocation had no handler.
- Fixed on PR #24 and merged as `71ed0106956e1e4d46fa47af9b2949c3e587b703`.
- Added regression coverage for onboarding-bot panel replies with inline buttons.
- Next: restart the Telegram runtime from current `main` and perform real Saved Messages, onboarding-bot, private-chat, and group verification.


## 2026-09-26 — Professional Panel v2
- User validation showed the previous panel was too flat and limited to master ON/OFF switches.
- Implemented PR #25: hierarchical Control Center with category → module → sub-capability navigation, durable parent/child state, global status, and Account/System section.
- Expanded the capability model to cover AI, Memory, Voice, Web, Plugins, PC Worker, Automation, Reminders, Tasks, Backup, Analytics, Learning, Multi-Agent, OCR, and Security sub-capabilities.
- PR #25 merged to main as d504af985246efa1480b73182b17c790a56bc175.
- Branch CI run 36266208463 passed on Python 3.11 and 3.12.
- Important limitation: panel controls are durable and enforceable through CapabilityService.require(), but individual domain execution paths still require their own gate wiring/provider verification before being considered fully operational.

## Next Task
1. Restart Telegram Runtime from merged main d504af985246efa1480b73182b17c790a56bc175.
2. Open /پنل and verify Main Menu → category → module → sub-capability navigation.
3. Verify parent OFF cascades to children and child toggles persist after reopening the panel.
4. Verify Account/System and Security pages.
5. Continue wiring domain execution paths to capability gates and real providers.


## 2026-09-26 — Internal Economy
- PR #27 merged as 508472022e61577a1597d016012893b31a891c14.
- Persistent wallet/ledger, transfer policy, admin adjustment, history, Telegram commands, migration 0004 and recipient resolution are implemented.
- Final CI passed on Python 3.11 and 3.12.
- Real database/Telegram runtime verification remains pending.


## 2026-09-26 — Panel Execution
- Completed PR #29: real execution for core utility/calculator capability gates.
- Regression: legacy /ping behavior preserved when the capability service is absent.

## 2026-09-26 — Myoi Adapter
- Completed PR #30: real Telegram transport adapter for @MeowieeeQBot.
- Adapter operates on visible Telegram messages/buttons rather than invented callback/API contracts.
- Next task: capture real Myoi bot observations with a linked account, then implement one workflow end-to-end with recorded evidence before expanding to the remaining Myoi modules.


## 2026-09-27 — External Database Persistence
- Added deployment-agnostic external SQL Server persistence support through `DATABASE_URL=mssql+pyodbc://...`.
- Added the missing durable migration covering Telegram sessions, domain state, security audit and diamond economy.
- Runtime startup now installs the SQL Server driver in the GitHub Windows workflow and verifies database connectivity after migration.
- Next: create/configure the operator's SQL Server Express instance, set the encrypted `DATABASE_URL` GitHub secret, run the runtime workflow, and verify migration + session reuse across a restart.


## 2026-09-30 — External SQL Server Persistence Task COMPLETE
- Operator-provided SQL Server Express database was reached successfully from the project environment.
- `DATABASE_URL` was configured privately; secrets were not emitted in test output.
- Python/SQLAlchemy/pyodbc connection returned the expected SQL Server database/login context.
- Alembic upgraded the real database from the initial schema through `0004_diamond_economy`.
- Real database inspection confirmed `alembic_version`, `domain_state`, `security_audit`, `telegram_accounts`, `tasks`, `system_metadata`, `diamond_wallets` and `diamond_transactions`.
- Encrypted Telegram session persistence smoke test: PASS.
- Runtime session reload smoke test across two `MultiUserTelegramRuntime` instances: PASS.
- Cleanup after the smoke test: PASS.
- Full local pytest after PR #37 merge: PASS.
- This task is complete; the active Telegram verification task remains separate and is not marked complete by the SQL Server evidence.


## 2026-10-01 — Panel Runtime Failure Investigation and Fix
- Real runtime /panel did not render because the onboarding bot's InlineQuery handler calls TelegramSessionStore.get_connected(), which requires the external SQL Server.
- Runtime logs showed ODBC Driver 18 error 08001 / TCP timeout to the private Tailscale SQL endpoint. Local PC tests confirmed SQL Server and port 1433 were reachable from the PC, but that did not prove continuous GitHub-runner reachability.
- Inline Mode was confirmed enabled; no Telegram session, encryption key, or credential regeneration was required.
- PR #42 merged as 750ed593ededda0c19ded9ac68dc76701c143689. It adds bounded initial connection retry/backoff, pool recycle/pre-ping resilience, SQL Server connect timeout, and environment configuration.
- CI run 36839640139: Python 3.11 PASS, Python 3.12 PASS.

## Next Task
1. Start the Telegram runtime from the merged main.
2. Send /پنل from Saved Messages and verify the panel actually appears.
3. Exercise nested category/module/sub-capability navigation and one parent/child toggle persistence cycle.
4. If the panel still fails, capture the new structured DB/Telegram runtime error rather than changing secrets.


## 2026-10-01 — Runtime Migration Failure Follow-up
- Fresh runtime run 36840274511 from merged main failed at Prepare database; Start Telegram bot was skipped.
- The failure was not a missing database schema and not a Telegram login/session problem. It was a GitHub-runner → Tailscale → SQL Server TCP timeout during Alembic migration startup.
- PR #43 merged as 02ac2504fb81792e969c636b2153808725e1ce37 and CI 36840788999 is green on Python 3.11/3.12.
- Next: run a fresh Telegram Bot Runtime from the new main, verify Prepare database passes and Start Telegram bot stays running, then send /پنل in Saved Messages.
- Do not regenerate Telegram session/secrets or expose SQL Server publicly.
