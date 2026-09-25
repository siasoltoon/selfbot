# Task State

## Active Task
Complete the first real multi-user Telegram onboarding verification using QR login.

## Status
IN PROGRESS — repeated `PhoneCodeExpiredError` proved the code-in-chat flow unsuitable; QR onboarding is implemented and CI-verified, and successful external QR onboarding is still pending.

## Latest Verified Implementation
- PR #14 implements multi-user onboarding and independent account runtime.
- PR #15 adds secure authentication lifecycle/error diagnostics.
- CI 36182724874 passed on Python 3.11 and 3.12.

## Latest QR Change
- PR #18 adds Telethon QR login as the production onboarding path.
- The onboarding bot sends a transient QR image, keeps the QR wait active before scanning, supports QR-triggered 2FA, deletes QR media after the challenge resolves, and persists the encrypted StringSession.
- Legacy phone/code methods remain only for compatibility and are no longer exposed by the onboarding bot.
- CI 36186445250 passed on Python 3.11 and 3.12.

## Latest Recovery Change
- Telegram `PhoneCodeExpiredError` no longer forces the user to restart the whole flow.
- `/resend` was initially implemented with a fresh client, but real testing showed `PhoneCodeExpiredError` persisted. The implementation is being corrected to reuse the existing transient client, preserving Telethon's internal phone-code hash so its `send_code_request()` can invoke `auth.resendCode`.
- The latest Telegram code delivery type/timeout metadata is logged without exposing the code or hash.
- Regression coverage verifies expired-code recovery and fresh-client replacement.

## Latest Diagnostic Change
- Authentication failures now log structured stage, Telegram exception type/module, sanitized exception message and traceback.
- Phone numbers are masked and owner IDs are fingerprinted.
- Login codes, 2FA passwords, phone_code_hash, API credentials and session material are not logged.
- Regression coverage verifies that sensitive test values are excluded from authentication error logs.

## Remaining Operator/Environment Work
1. Merge PR #18 after the green CI evidence.
2. Run real Telegram `/connect` using QR and another already-authorized Telegram device.
3. If QR authentication fails, capture the exact sanitized Telegram exception before making another targeted change.
4. Verify encrypted session persistence and linked-account message routing.
4. Continue the broader external verification matrix: providers, worker, OCR, DB, backup/restore, deployment, performance and security.

## Rule
Do not fabricate PASS for environment-dependent checks. Any failure discovered there becomes a new targeted engineering task.
