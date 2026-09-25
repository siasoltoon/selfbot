# Task State

## Active Task
Diagnose and complete the first real multi-user Telegram onboarding verification.

## Status
IN PROGRESS — Telegram runtime exposed `PhoneCodeExpiredError`; recovery hardening is implemented and CI-verified; successful external onboarding is still pending.

## Latest Verified Implementation
- PR #14 implements multi-user onboarding and independent account runtime.
- PR #15 adds secure authentication lifecycle/error diagnostics.
- CI 36182724874 passed on Python 3.11 and 3.12.

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
1. PR #17 resend-protocol correction is merged and CI-verified.
2. Repeat real Telegram `/connect` flow against the merged main branch and capture sanitized runtime result.
3. If authentication still fails, identify the exact Telegram exception before making another targeted change.
3. Verify successful session persistence and linked-account message routing.
4. Continue the broader external verification matrix: providers, worker, OCR, DB, backup/restore, deployment, performance and security.

## Rule
Do not fabricate PASS for environment-dependent checks. Any failure discovered there becomes a new targeted engineering task.
