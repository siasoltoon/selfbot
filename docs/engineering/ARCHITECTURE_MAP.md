# Architecture Map

## Current Phase
Phase 2 core foundation.

## Implemented
- Python 3.11+ package foundation
- validated environment configuration
- unified error taxonomy
- SQLAlchemy engine/session boundary
- Alembic migration boundary
- bootstrap metadata model
- structured secret-safe logging
- deployment-neutral runtime bootstrap
- automated tests and CI

## Defined
Telegram Client Adapter -> Event Router -> Core Application -> Command/Task/Scheduler Services -> Plugin Runtime -> Durable Persistence -> Local Worker / Optional PC Worker -> External Service Adapters

Administration API:
FastAPI -> Auth/Validation -> Core Services -> Persistence/Adapters

## Next Implementation Boundaries
- normalized internal event envelope
- command registry
- durable task lifecycle
- scheduler
- plugin lifecycle
- Telegram adapter
- API
- worker protocol

## Deployment
Deployment-neutral core supporting Railway, VPS, temporary/limited-runtime environments and personal PC/Laptop. Provider-specific behavior remains in infrastructure/configuration.
