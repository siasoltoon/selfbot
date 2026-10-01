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


## Professional Telegram Panel v2 — 2026-09-26
- PR #25 branch CI run 36266208463 — PASS on Python 3.11 and 3.12.
- Compileall — PASS on both versions.
- Pytest — PASS on both versions; branch reached 81 passing tests.
- New tests cover hierarchical categories, parent/child cascade behavior, core Security/Tasks invariants, and onboarding-bot panel rendering.
- Real Telegram v2 UI interaction is NOT yet claimed PASS; runtime must be restarted from the merged main commit and operator must exercise the nested navigation.


## Internal Economy — 2026-09-26
- PR #27 initial CI exposed three failures; capability scope and a test fixture were corrected.
- Final Python 3.11 and 3.12 checks passed; compileall passed on both.
- Focused tests cover fees, limits, self-transfer, insufficient balance, admin authorization, non-negative balances and Telegram balance/transfer routing.
- Real PostgreSQL and real Telegram transaction execution remain NOT_RUN.


## 2026-09-26 — Panel Runtime
- PR #29 final CI: Python 3.11 PASS, Python 3.12 PASS, all four workflow checks green.
- Tests cover disabled/enabled calculator, ping, today, ID and owner-wide cancellation behavior.

## 2026-09-26 — Myoi Adapter
- PR #30 final CI: Python 3.11 PASS and Python 3.12 PASS across all four checks.
- Tests cover real adapter boundaries with a fake Telethon-like client: bot resolution, command sending, visible button discovery and click.
- Live @MeowieeeQBot observation has NOT yet been claimed PASS.


## 2026-09-27 — External Database Persistence
- PR #33 SQL Server persistence implementation: CI validation passed on Python 3.11 and 3.12 after fixing test-file newline encoding.
- SQLite Alembic regression now verifies all durable tables, including Telegram accounts and diamond economy.
- Real SQL Server migration/connectivity remains NOT_RUN until an operator-provided SQL Server endpoint is reachable.


## 2026-09-30 — External SQL Server Verification
- Local environment had `ODBC Driver 18 for SQL Server` available and `Test-NetConnection 127.0.0.1 -Port 1433` succeeded.
- SQLAlchemy connection test through `mssql+pyodbc` succeeded against the configured SQL Server database.
- `python -m alembic upgrade head` completed successfully through `0004_diamond_economy`.
- SQL Server schema inspection confirmed all expected durable tables; `dbo.alembic_version` reported `0004_diamond_economy`.
- Encrypted Telegram session persistence smoke test: `DB_PERSISTENCE_WRITE=PASS` and `DB_PERSISTENCE_CLEANUP=PASS`.
- Runtime reload smoke test: `SQLSERVER_RUNTIME_RELOAD=PASS` and `SQLSERVER_RUNTIME_RELOAD_CLEANUP=PASS`.
- PR #37 CI run 36697168438 passed; PR #37 merged as `65594754cdfed7e2e0cd6006d55c5e464ebaa1d8`.
- Full local `python -m pytest -q` after the merge: PASS with no failures.
- The runtime reload smoke test intentionally used a fake Telegram client, so it proves durable session reconstruction but does not replace a real Telegram reconnect test.


## 2026-10-01 — Runtime DB Resilience
- PR #42 CI run 36839640139 — PASS on Python 3.11 and Python 3.12.
- Compileall passed on both versions.
- Full pytest passed on both versions after fixing two CI-discovered regressions during implementation: bootstrap newline syntax and backward-compatible Settings constructor defaults.
- Added regression coverage for environment-configured database retry settings.
- Real Telegram panel interaction is still NOT PASS; it requires a fresh runtime from merged main and operator-side /پنل verification.


## 2026-10-01 — Runtime Migration Failure and Fix
- Runtime workflow 36840274511 — FAIL at Prepare database; Start Telegram bot was SKIPPED.
- Job log: ODBC Driver 18 error 08001 / TCP Provider timeout 258 while Alembic connected to 100.114.8.105:1433.
- PR #43 CI 36840788999 — PASS on Python 3.11 and 3.12 after adding migration connection retry coverage and correcting one test formatting regression.
- PR #43 merge commit: 02ac2504fb81792e969c636b2153808725e1ce37.
- Real /پنل interaction remains NOT_RUN after PR #43 because the runtime did not reach bot startup.


## 2026-10-01 — Persisted Session Restore
- Runtime 36841201279: FAIL only at Start Telegram bot after database migration succeeded.
- Exact failure: `sqlite3.OperationalError: unable to open database file` from Telethon `SQLiteSession` because a persisted StringSession payload was passed as a filename.
- PR #44 CI run 36841546134 — PASS.
- PR #44 merged as `fd2cbf8c1e9a9b682b942a69546b585310624a7c`.
- Added regression test verifying persisted runtime client construction uses `StringSession`.
- Real Telegram runtime/panel verification remains NOT_RUN after the fix.


## 2026-10-01 — Runtime #22 investigation and PR #45
- Runtime 36841836347 was cancelled by the operator after commands appeared unresponsive.
- Post-cancellation logs proved application started and repeated Telethon Got difference updates, so Telegram startup itself was not stuck.
- The log contained a SQL Server 08S01 Communication link failure during the panel/account lookup path, specifically while SQLAlchemy attempted SQLEndTran.
- PR #45 CI run 36845834506 — PASS on Python 3.11 and Python 3.12; compile and pytest steps passed.
- Added regression coverage for read-only database session semantics and event-handler failure diagnostics.
- Real runtime /status, /panel, /پنل, linked-account routing and restart/session reuse remain NOT_RUN after PR #45 and require a fresh runtime.


## 2026-10-01 — Telegram Runtime Incident Evidence
- GitHub Actions runtime reached application startup and received Telegram updates.
- /panel failure was captured with EventRouter correlation ID and exact exception type after PR #45 logging hardening.
- SQL Server failures observed: ODBC 08S01/08001 connectivity timeout while querying durable state.
- Telegram transport failure observed: ValueError from Telethon entity lookup for numeric chat ID represented as a string.
- PR #46 adds regression tests for input-chat entity propagation and numeric chat-ID normalization.
- CI result for PR #46 must be recorded after GitHub Actions completes; no PASS is claimed yet.


## 2026-10-01 — PR #46 PASS
- CI run 36848464965 passed on Python 3.11 and 3.12.
- Compileall passed on both versions.
- Pytest passed on both versions; 105 tests passed in the successful run.
- Regression coverage includes input chat entity propagation and numeric chat-ID transport.
- Runtime SQL Server/Tailscale reliability and real Telegram UI interaction remain environment-dependent and are not claimed PASS by CI.


## 2026-10-01 — PR #47 Diagnostic Validation
- CI run 36850285954: PASS on Python 3.11 and Python 3.12.
- Diagnostic workflow code is covered by normal compile/test CI, but real GitHub Runner → PC SQL connectivity remains environment-dependent and is NOT claimed PASS by CI.
- The next evidence source is a manually triggered Telegram Bot Runtime run containing the new Tailscale/TCP/SQL diagnostic output.

## 2026-10-01 — Telegram Runtime connectivity evidence
- Run 36850880589 on main: initial TCP/Tailscale/SQL preflight PASS; Alembic PASS; Telegram startup/connect PASS.
- During runtime: SQL access failed with ODBC 08S01/10060 communication-link timeout and 08001/258 login timeout to 100.114.8.105:1433.
- `/panel` failure was logged as `telegram capability panel command failed` with the same DB connectivity error.
- `/status` did not produce a usable response according to operator test.
- Result: real runtime DB connectivity NOT PASS; Telegram panel/status NOT PASS.
- PR #48 adds continuous live Tailscale/TCP evidence; no PASS is claimed until a fresh runtime proves stable connectivity.

