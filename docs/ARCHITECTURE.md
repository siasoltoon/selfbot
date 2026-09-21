# System Architecture

## 1. Purpose
This document defines the target architecture for the Telegram Personal AI Operating System. It is an architecture contract, not a claim that all described components are already implemented. The implementation must evolve phase-by-phase from the repository's validated state.

## 2. Technology Stack
### Runtime
- Python 3.11+.
- setuptools packaging with a src/ layout.
- pytest for automated tests.

### Telegram
- Telethon as the user-client boundary for Telegram Self Bot behavior.
- Telegram-specific code stays behind a client adapter.

### Core application
- Typed Python domain/service modules.
- Pydantic for structured external/configuration validation.
- SQLAlchemy 2.x for persistence abstraction.
- Alembic for schema migrations.
- SQLite as the default local/development database.
- PostgreSQL as the production-capable external database option.

### HTTP/API
- FastAPI for the administration/API boundary.
- Uvicorn as the ASGI runtime.
- API schemas remain separate from domain models.

### Queue and background execution
- Durable database-backed task state is the source of truth.
- Lightweight in-process workers are allowed for tasks that do not require a PC Worker.
- Optional PC Worker execution uses an explicit authenticated protocol.
- Redis is not a mandatory core dependency; it may be introduced later only when measured workload requirements justify it.

### Operations
- Structured standard-library logging initially, behind a stable application logging facade.
- Docker and Docker Compose for portable deployment.
- Environment variables for secrets and deployment configuration.

## 3. Logical Architecture
Telegram Client Adapter -> Event Router -> Core Application -> Plugin Runtime -> Durable Task State -> Local Worker / Optional PC Worker -> External Services -> Persistence

The administration API reads and mutates the same application services rather than duplicating business logic.

## 4. Layer Rules
### Adapters
External protocols and libraries live here: Telegram, HTTP providers, PC Worker transport, filesystem and external databases.

### Domain/Core
Contains business rules and use cases: events, commands, permissions, tasks, scheduling, memory, automation and plugin lifecycle. Core modules must not import deployment-specific modules.

### Persistence
Repositories/data-access services translate domain operations to database operations. Domain services must not contain deployment-specific SQL.

### API
FastAPI routes validate input, authorize the caller, invoke core services and serialize results. Routes must not implement business rules.

### Plugins
Plugins use declared capabilities and stable core interfaces. A plugin must not bypass security, persistence or task lifecycle controls.

### Workers
A worker is an optional execution target. Worker absence is represented explicitly and cannot become a fabricated success result.

## 5. Event and Task Flow
EVENT -> validate -> authorize -> route -> condition/use-case -> create task when needed -> execute locally or claim worker execution -> record result -> audit/log

Heavy work should be deferred instead of blocking the Telegram event path.

## 6. Deployment Model
The architecture is deployment-neutral: the same application package is deployable in Railway, standard VPS, temporary/limited-runtime server environments and personal PC/Laptop.

Deployment differences belong in environment variables, Docker/Compose files, service definitions, infrastructure adapters and startup configuration. No core module may branch on a provider-specific deployment name to implement business behavior.

## 7. Runtime Modes
### Local lightweight mode
Core, Telegram client, database and lightweight workers run on one machine.

### Core + PC Worker mode
Telegram/core services run on a server while heavy jobs are delegated to an authenticated PC Worker.

### All-local development mode
The same services can run locally without a cloud provider.

Worker availability is observable and explicit in all modes.

## 8. Reliability Boundaries
Every external boundary must have timeout, validation, structured error classification, safe failure, retry policy where appropriate and audit/diagnostic logging. No external failure may silently produce a successful action result.

## 9. Evolution Rules
- Prefer interfaces/adapters over provider-specific coupling.
- Introduce dependencies only when their phase requires them.
- Do not implement later-phase capabilities in the architecture task.
- Any deviation from this design must be recorded in DECISIONS.md.
