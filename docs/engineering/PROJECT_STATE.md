# Project State

## Current Position
- Roadmap: Phases 1-25 code-side implementation/hardening sweep completed.
- Status: IN PROGRESS — final external verification gate.
- Latest merged implementation: PR #11, merge commit a29ff2f56047c2b8b6873ca89d48ee8f91040c78.
- CI: run 35614933655 PASS on Python 3.11 and 3.12.

## Completed Code-Side Work
- Phases 0-3 foundation/plugin system.
- Phases 4-10 core capability boundaries.
- Phases 11-20 capability services, composition, durable domain-state boundary and migrations.
- Phase 21 OCR benchmark framework.
- Phase 22 adversarial/failure harness.
- Phase 23 Persian/English UX validation and bounded pagination.
- Phase 24 production-hardening evidence model.
- Phase 25 final-release audit model.

## Final External Verification Gate
The repository does not claim production release merely from framework/unit/CI evidence. Remaining work requires real credentials, real Telegram/provider behavior, labeled OCR data, real worker transport, deployed environments, backup/restore, performance/load and rollback/recovery evidence.

## Latest Runtime Integration
- Added deployment-agnostic `scripts/run_bot.py` entrypoint.
- Added manual GitHub Actions Windows runtime workflow.
- Workflow applies Alembic migrations and starts the bot process on every manual run.
- Inspected `siasoltoon/vps`: retained its Windows-runner pattern, but did not copy hardcoded credentials or unsafe RDP authentication settings.
- Telegram StringSession secrets are now supported explicitly.
- CI run 36177272784 PASS on Python 3.11/3.12.

## Next
Configure the required GitHub Actions secrets and execute the first real Telegram runtime verification. Then record the result and continue the remaining external verification matrix.
