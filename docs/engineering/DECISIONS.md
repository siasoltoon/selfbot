# Engineering Decisions

## 2026-09-21 — Python foundation
Python 3.11+ is the baseline runtime.

## 2026-09-21 — Telegram adapter
Telethon is the Telegram user-client implementation behind an adapter boundary. Core services do not depend on Telethon event types.

## 2026-09-21 — Persistence
SQLAlchemy 2.x plus Alembic is the persistence/migration stack. SQLite is the default local database; PostgreSQL is production-capable.

## 2026-09-21 — Deployment neutrality
Railway, VPS, limited-runtime environments and personal PC/Laptop remain infrastructure concerns.

## 2026-09-21 — Optional worker
PC Worker is optional infrastructure and never a hidden core startup dependency. Worker execution must be explicit and verifiable.

## 2026-09-21 — Plugin isolation
Plugins use stable core interfaces and declared permissions/capabilities. Plugin metadata cannot grant authorization.

## 2026-09-21 — Provider-neutral AI/voice/web
AI, STT/TTS and web search use replaceable provider contracts. Missing providers must fail explicitly rather than fabricate results.

## 2026-09-21 — Web safety
Web retrieval accepts HTTPS only, enforces response size limits and blocks private/loopback/link-local destinations before retrieval.

## 2026-09-21 — Worker truth
A worker job is never marked succeeded merely because dispatch was requested. Unsupported capabilities become deferred and offline state is explicit.

## 2026-09-21 — Engineering memory
Continuation state under docs/engineering is authoritative and updated after meaningful validated work.
