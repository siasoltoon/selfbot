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