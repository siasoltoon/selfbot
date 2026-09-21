# Engineering Decisions

## 2026-09-21 — Python foundation
Python 3.11+ is the baseline runtime. It keeps the bootstrap dependency-light and supports the planned service architecture.

## 2026-09-21 — Telegram adapter
Telethon is the planned Telegram user-client implementation behind an adapter boundary. Core services must not depend directly on Telethon event types.

## 2026-09-21 — Persistence
SQLAlchemy 2.x plus Alembic is the planned persistence/migration stack. SQLite is the default local database; PostgreSQL is the production-capable option.

## 2026-09-21 — API
FastAPI is the planned administration/integration API framework. API routes invoke core services instead of duplicating business logic.

## 2026-09-21 — Deployment neutrality
Deployment targets are infrastructure/configuration concerns, not core business-logic branches. The same application remains portable across Railway, VPS, limited-runtime environments and personal PC/Laptop.

## 2026-09-21 — Optional worker boundary
PC Worker integration is optional infrastructure and is not a core startup dependency. Worker execution is explicit and cannot be represented as success without an actual result.

## 2026-09-21 — Durable task truth
Database-backed task state is the source of truth. An in-process worker can handle lightweight work, while heavy work may be delegated to a PC Worker.

## 2026-09-21 — Plugin isolation
Plugins use stable core interfaces and declared permissions/capabilities. Plugin metadata cannot grant itself authorization.

## 2026-09-21 — Engineering memory
Continuation state under docs/engineering is authoritative and updated after meaningful validated work.
