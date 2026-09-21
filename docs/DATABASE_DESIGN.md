# Database Design

## 1. Goals
The database provides durable state for the core application while remaining portable between local development and production deployments.

## 2. Database Technology
- SQLAlchemy 2.x is the persistence abstraction.
- Alembic manages schema migrations.
- SQLite is the default development/local database.
- PostgreSQL is the production-capable external database.
- Database URLs are configuration values and never hardcoded.

## 3. Logical Domains
The schema is divided logically into users, settings, plugins, tasks, task attempts, events/audit records, AI memory, analytics, automation rules, storage metadata and worker registrations. Exact physical tables are introduced during the corresponding implementation phases.

## 4. Core Invariants
### Identity
Every persisted user-owned record has a stable owner/user relationship where applicable.

### Tasks
Task state transitions are explicit. A task cannot be marked successful unless an execution result exists.

### Worker jobs
Worker execution records task/job identifier, worker identity, claim token or equivalent ownership proof, claim time, heartbeat/lease information, execution state and result/classified failure.

### Memory
Memory records require category, ownership/scope and lifecycle metadata. Forget/delete operations must be auditable without retaining deleted content unnecessarily.

## 5. Migration Rules
- Schema changes use Alembic migrations.
- No production schema mutation is performed by ad-hoc startup code.
- Migrations must be forward-compatible with the supported deployment process.
- Destructive migrations require explicit review and backup considerations.

## 6. Indexing Strategy
Indexes will be added for measured lookup paths such as owner/user identifiers, task status and scheduling time, worker status/heartbeat, plugin identifier, memory category/search metadata and audit event time/type. Avoid broad indexes without evidence of need.

## 7. Transactions
Use transactions around state transitions that must be atomic: task claiming, permission-sensitive mutations, plugin enable/disable, worker result commits and security/emergency-lock changes.

External side effects are not assumed transactional with the database. Use explicit execution states and recovery logic.

## 8. Backup Compatibility
Backups identify schema version, application version, creation timestamp and integrity metadata. Restore validates schema/version/integrity before mutating live state.

## 9. Portability
Application services use repositories/units of work rather than SQLite-specific SQL. SQLite-specific behavior is isolated to the database adapter/configuration.
