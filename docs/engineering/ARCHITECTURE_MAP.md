# Architecture Map

## Current Phase
Phase 1 architecture design complete; Phase 2 implementation is next.

## Implemented Foundation
- Python 3.11+ package foundation
- environment-backed configuration
- optional worker configuration
- automated tests
- GitHub Actions CI

## Defined Architecture
Telegram Client Adapter
-> Event Router
-> Core Application
-> Command/Task/Scheduler Services
-> Plugin Runtime
-> Durable Persistence
-> Local Worker / Optional PC Worker
-> External Service Adapters

Administration API:
FastAPI -> Auth/Validation -> Core Services -> Persistence/Adapters

## Planned Persistence
- SQLAlchemy 2.x
- Alembic migrations
- SQLite local/default
- PostgreSQL production-capable option

## Planned Integration Boundaries
- Telethon Telegram adapter
- FastAPI API adapter
- authenticated PC Worker protocol
- plugin lifecycle/manifest boundary
- repository/unit-of-work persistence boundary

## Deployment
Deployment-neutral core supporting Railway, VPS, temporary/limited-runtime environments and personal PC/Laptop. Provider-specific behavior belongs in infrastructure/configuration.

## Status
Architecture is documented; implementation begins in Phase 2.
