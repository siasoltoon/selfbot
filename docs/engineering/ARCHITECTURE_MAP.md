# Architecture Map

Telegram Adapter
-> Event Router
-> Core Services
-> Domain Capability Services
-> Task Manager / Scheduler
-> Persistence
-> optional Worker / external providers

Admin/API/UI, Telegram, AI, voice, web, OCR and worker transports remain adapters around provider-neutral core contracts.

## New Integration Boundaries
- DomainStore + SQLAlchemy models for durable domain state.
- Alembic migrations for schema evolution.
- OCRBenchmark for measured OCR evaluation.
- AdversarialHarness for explicit failure testing.
- UXValidator for Persian/English Telegram response constraints.
- ReleaseAudit for production evidence tracking.

## Deployment Rule
Core logic remains deployment-neutral. Railway/VPS/personal-PC behavior belongs in environment configuration and infrastructure adapters.
\n\n## Deployment Runtime\n- `scripts/run_bot.py` is the shared process entrypoint.\n- `.github/workflows/telegram-runtime.yml` is a deployment adapter for GitHub-hosted Windows runners.\n- Core application logic remains deployment-agnostic.\n

## Multi-user Telegram path
Installation Bot → Authentication Service → encrypted Session Store → Multi-user Telegram Runtime → Event Router → Core Services.

The installation bot is a normal Telegram bot account. Each connected user's selfbot account is an independent Telethon client. Persistent account sessions are encrypted at rest; transient login code/2FA input is not persisted or dispatched to the core event bus.
