# Engineering Decisions

- Python 3.11+ baseline.
- SQLAlchemy 2.x + Alembic for persistence/migrations.
- SQLite default local database; PostgreSQL supported through configuration.
- Telethon confined to Telegram adapter.
- PC Worker is optional and must report explicit availability.
- Provider-neutral AI/voice/web/OCR contracts; missing providers never produce fake success.
- Controlled learning is approval-gated.
- Backup payloads use deterministic checksums before restore acceptance.
- Phase 21 metrics are measured only from supplied labeled cases; no synthetic score is presented as real performance.
- Phase 22 failures are explicit outcomes; the harness never converts an exception into a claimed correct answer.
- Phase 23 Persian UX requires explicit RTL metadata.
- Phase 24/25 release status is evidence-driven; NOT_RUN/BLOCKED evidence prevents final release pass.

## Decision: Multi-user Telegram onboarding
- Use a normal BotFather bot for onboarding and independent Telethon user clients for linked accounts.
- Accept phone number, Telegram login code, and optional 2FA password only as transient authentication input.
- Persist only the resulting Telethon StringSession, encrypted at rest with a deployment-provided Fernet key.
- Do not rely on GitHub-hosted runner local SQLite for durable multi-user sessions; persistent PostgreSQL is the intended runtime store.
- Keep the legacy single-session adapter available for compatibility while multi-user mode is enabled by onboarding token + session encryption key.

## Decision: Telegram authentication code recovery
- Treat `PhoneCodeExpiredError` and `PhoneCodeInvalidError` as recoverable interaction errors while the transient login remains valid.
- Preserve the pending flow rather than forcing a complete /connect restart.
- Explicit /resend reuses the existing transient Telethon client so its internal phone-code hash is preserved and `send_code_request()` can use Telegram's `auth.resendCode` protocol. A new client would lose that protocol state and start a new authorization request.
- Never automatically loop/resend codes on failure; Telegram-side rate limits remain authoritative.

## Decision: Telegram authentication diagnostics
- Authentication failures must expose enough structured runtime evidence to identify the Telegram exception and failing stage without exposing authentication secrets.
- Log masked phone numbers and hashed owner identifiers rather than raw personal/account identifiers.
- Redact login codes, 2FA passwords, phone_code_hash, API credentials and session material from exception messages.
- Preserve the original exception type for programmatic handling and keep user-facing errors generic until the exact failure is understood.

## Decision: QR-first Telegram onboarding
- Real runtime testing showed repeated `PhoneCodeExpiredError` even with the corrected resend protocol; observed delivery type was `SentCodeTypeApp`.
- Telethon documents `qr_login()` plus `QRLogin.wait()` as a supported login flow; the wait must run while the QR is being scanned.
- The onboarding bot generates the QR image in memory, sends it as short-lived Telegram media, removes the QR message after completion/expiry/failure, and never logs the QR URL/token.
- QR login may require the account's 2FA password after scanning; it remains transient and is never persisted or logged.
- A second already-authorized Telegram device is required to scan the QR shown by the onboarding bot; same-device phone-only onboarding is not claimed as supported by this transport.

## Decision: QR post-scan 2FA lifetime
- The real QR test reached `SessionPasswordNeededError` after QR acceptance, then the transient client was disconnected before 2FA completion because the original QR expiry remained active.
- The failure was a lifecycle timeout, not evidence of an invalid 2FA password.
- After QR acceptance with 2FA required, extend the pending transient session deadline to the configured authentication-service TTL.
- Keep the 2FA password transient and out of logs/storage.
- If future lifecycle states make one `expires_at` field ambiguous, split QR and post-scan 2FA deadlines into separate fields rather than overloading one timestamp.

## Decision: Post-auth session persistence safety
- Use Telethon `StringSession()` for transient QR authentication clients so successful login always has a serializable session representation.
- Treat encrypted durable session persistence as part of the application-level authentication transaction.
- If Telegram authentication succeeds but persistence fails, attempt `log_out()` before disconnecting the authenticated client; never silently leave an authenticated session unmanaged.
- Distinguish invalid 2FA credentials from infrastructure/persistence failures in user-facing onboarding responses.

## Decision: Global Telegram capability panel
- Use /panel and /پنل on the linked user account rather than restricting the panel to the onboarding bot's private chat.
- Accept outgoing commands only for control actions; incoming group messages cannot control the owner account.
- Use the onboarding bot's Inline Mode to deliver the interactive panel into the exact originating chat, including Saved Messages. This is necessary because Telethon callback buttons are bot-side interactions.
- Authenticate panel ownership with an HMAC-derived compact token and verify the callback sender before changing state.
- Reuse the existing encrypted-session secret as the signing secret; no new secret is introduced.
- Persist capability settings through DomainStore/domain_state rather than adding a duplicate settings table.
- Separate capability enabled state from dependency availability. A toggle never creates a fake provider/worker result.
- Security and task/scheduler remain always enabled to preserve recovery and core safety controls.
