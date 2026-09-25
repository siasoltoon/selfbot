# Task State

## Active Task
Complete the first real multi-user Telegram onboarding verification using QR login, including the post-scan 2FA path.

## Status
IN PROGRESS — the real QR test reached Telegram acceptance and 2FA, then Telegram created an authenticated session but application-side StringSession persistence failed. PR #20 fixed the persistence mechanism; PR #21 additionally revokes an authenticated session if durable persistence fails. Both are CI-verified and merged. A fresh real test is now required.

## Latest Verified Implementation
- PR #14 implements multi-user onboarding and independent account runtime.
- PR #15 adds secure authentication lifecycle/error diagnostics.
- PR #18 adds Telethon QR login as the production onboarding path.
- PR #19 extends the pending session lifetime when QR authentication succeeds and Telegram requests 2FA.
- PR #19 CI run 36187266466 passed on Python 3.11 and 3.12 and was merged to main as 76a4e9d2887f1bebfee9eb0c5b5c5f5486294787.
- PR #20 CI run 36187991097 passed and was merged to main as 1a74d35d44f958466f9d16eab903253fbbf96fc0.
- PR #21 first CI run 36188334722 failed because its new regression expected the pre-wrap RuntimeError; the test was corrected to expect DependencyError. PR #21 CI run 36188868237 then passed on Python 3.11 and 3.12 and was merged to main as df5b27344bcc498d252c4e5786119ca0702fa1fc.

## Real QR Test Diagnosis
- QR generation, upload, scan and Telegram-side acceptance all succeeded.
- Telegram then raised `SessionPasswordNeededError`, proving the account reached the 2FA stage.
- The QR challenge had a short remaining TTL; the pending item's `expires_at` was not extended after the QR was accepted.
- Cleanup subsequently disconnected the transient client while the user was entering 2FA, producing the generic onboarding failure message.
- This was a lifecycle timeout bug, not evidence that the supplied 2FA password was incorrect.
- PR #19 changes `expires_at` to `time.monotonic() + ttl_seconds` when 2FA is requested and adds a regression test with a 1-second QR TTL and 5-second post-scan lifetime.

## Remaining Operator/Environment Work
1. Run real Telegram `/connect` against current main using QR and another already-authorized Telegram device.
2. If 2FA is requested, enter the account's 2FA password and verify that onboarding completes without the transient client being cleaned up.
3. Verify encrypted StringSession persistence.
4. Verify linked-account message routing.
5. Continue the broader external verification matrix: providers, worker, OCR, DB, backup/restore, deployment, performance and security.

## Rule
Do not fabricate PASS for environment-dependent checks. Any failure discovered there becomes a new targeted engineering task.
