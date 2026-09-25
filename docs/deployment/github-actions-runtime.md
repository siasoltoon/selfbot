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
