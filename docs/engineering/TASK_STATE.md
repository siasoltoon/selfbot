# Task State

## Active Task
Phases 1-25 — implementation/hardening sweep complete for code-side work that can be performed without external operator credentials or production infrastructure.

## Status
IN PROGRESS — verification gate

## Completed In This Sweep
- Composed Phase 11-20 services into CoreServices.
- Added durable domain-state repository.
- Added domain-state and security-audit ORM models.
- Added Alembic initial and Phase 11-20 migrations.
- Added Phase 21 provider-neutral OCR benchmark metrics.
- Added Phase 22 adversarial/failure harness.
- Added Phase 23 Persian/English UX validation and pagination.
- Added Phase 24 production evidence model.
- Added Phase 25 final release audit model.
- Added focused tests for the above.

## Operator-Only / Environment-Dependent Work
1. Real Telegram login/session and message-flow verification.
2. Real AI/STT/TTS/search provider credentials and provider behavior.
3. Real PC Worker transport, heartbeat, claim/retry and offline recovery.
4. Labeled OCR image dataset and actual OCR provider benchmark.
5. Real deployment startup, health, restart and rollback checks.
6. Real backup/restore against deployed data.
7. Load/performance evidence on the target deployment.
8. Final security/dependency audit in the target environment.

## Rule
Do not mark final release COMPLETE until CI, integration, deployment and recovery evidence are all green.
