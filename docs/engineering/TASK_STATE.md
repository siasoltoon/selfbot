# Task State

## Active Task
Complete the first real multi-user Telegram onboarding verification using QR login, including the post-scan 2FA path.

## Status
IN PROGRESS — the first real QR test successfully reached Telegram QR acceptance and 2FA, but the transient client was disconnected before 2FA completion because the original QR TTL was reused. PR #19 fixed and CI-verified that lifecycle bug; a fresh real test is now required.

## Latest Verified Implementation
- PR #14 implements multi-user onboarding and independent account runtime.
- PR #15 adds secure authentication lifecycle/error diagnostics.
- PR #18 adds Telethon QR login as the production onboarding path.
- PR #19 extends the pending session lifetime when QR authentication succeeds and Telegram requests 2FA.
- PR #19 CI run 36187266466 passed on Python 3.11 and 3.12 and was merged to main as 76a4e9d2887f1bebfee9eb0c5b5c5f5486294787.

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
