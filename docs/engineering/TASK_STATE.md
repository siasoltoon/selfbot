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
