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
- Preserve the pending flow rather than forcing a complete `/connect` restart.
- Explicit `/resend` reuses the existing transient Telethon client so its internal phone-code hash is preserved and `send_code_request()` can use Telegram's `auth.resendCode` protocol. A new client would lose that protocol state and start a new authorization request. This was corrected after real testing showed the fresh-client approach still produced `PhoneCodeExpiredError`.
- Never automatically loop/resend codes on failure; Telegram-side rate limits remain authoritative.

## Decision: Telegram authentication diagnostics
- Authentication failures must expose enough structured runtime evidence to identify the Telegram exception and failing stage without exposing authentication secrets.
- Log masked phone numbers and hashed owner identifiers rather than raw personal/account identifiers.
- Redact login codes, 2FA passwords, phone_code_hash, API credentials and session material from exception messages.
- Preserve the original exception type for programmatic handling and keep user-facing errors generic until the exact failure is understood.
