# GitHub Actions runtime

The repository can run the same deployment-agnostic application on a GitHub
Actions Windows runner. The runtime workflow is manual so a run explicitly
starts one bot process.

## Required GitHub Actions secrets

Configure these repository secrets before the first runtime run:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION` — Telethon StringSession for the Telegram account
- `OWNER_ID` — numeric Telegram user ID of the owner

Do not commit any of these values.

## Start

Open **Actions → Telegram Bot Runtime (GitHub Actions) → Run workflow**.

The job installs the application, applies database migrations, and starts the
same `scripts/run_bot.py` entrypoint used by other deployment targets.

## Important runtime limitation

GitHub-hosted runners are temporary. The workflow keeps the bot process alive
only for the lifetime allowed by the hosted runner/job. A cancelled, expired,
or failed job stops the bot. This is suitable for runtime testing and
temporary operation, not a durable 24/7 production host.

The previous `siasoltoon/vps` workflow was inspected and its Windows-runner
pattern was retained, but its hardcoded RDP password and disabled RDP
authentication are deliberately not copied into this project.


## Multi-user Telegram onboarding

The runtime now supports a normal Telegram onboarding bot plus independent user-account sessions.

Required GitHub Actions secrets for multi-user mode:
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_ONBOARDING_BOT_TOKEN`
- `TELEGRAM_SESSION_ENCRYPTION_KEY` (Fernet key)
- `DATABASE_URL` pointing to a persistent PostgreSQL database for durable multi-user sessions

Optional:
- `OWNER_ID` is not required for linked-account routing.
- `TELEGRAM_SESSION` remains supported only for the legacy single-session runtime.

User flow:
1. User opens the onboarding bot and sends `/connect`.
2. User sends the phone number in international format.
3. The bot requests the Telegram login code.
4. If Telegram requires 2FA, the bot requests the 2FA password.
5. The code and 2FA password are transient only; they are not written to the database or application event bus.
6. The resulting Telethon StringSession is encrypted before persistence.
7. The connected account is loaded as an independent runtime client.

Security requirements:
- Never print login codes, 2FA passwords, or decrypted StringSessions to logs.
- Treat the encryption key and database as production secrets.
- A Telethon session is equivalent to an authenticated credential; anyone who obtains it may be able to access the account.
- GitHub-hosted runners are ephemeral. SQLite on the runner is only suitable for temporary verification; use persistent PostgreSQL for real multi-user operation.

The onboarding bot is a normal BotFather bot and is separate from the user selfbot accounts.
