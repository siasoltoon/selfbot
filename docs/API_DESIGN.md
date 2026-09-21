# API Design

## Purpose
The API is the administration and integration boundary for the core application. It exposes application services without duplicating domain logic. FastAPI is the planned HTTP framework.

## Layers
HTTP Request -> Authentication -> Request Validation -> Authorization -> Application Service -> Repository/External Adapter -> Response Schema

Routes remain thin.

## Versioning
Use an explicit version prefix, initially /api/v1. Breaking contract changes require a new version or an explicit migration strategy.

## Endpoint Groups
Planned groups:
- /api/v1/health
- /api/v1/status
- /api/v1/tasks
- /api/v1/plugins
- /api/v1/workers
- /api/v1/security
- /api/v1/settings
- /api/v1/audit

Exact endpoints are implemented only in their corresponding feature phases.

## Authentication and Authorization
Authentication is separate from authorization. The API authenticates the caller, resolves role/capabilities, authorizes the operation and rejects unauthorized actions before side effects. Sensitive endpoints are owner-only unless explicitly delegated.

## Response Contract
Use stable structured schemas containing status, typed payload and classified error information where applicable. Include correlation/request identifiers where useful. Never expose stack traces, credentials or raw provider secrets.

## Error Contract
Classify errors into validation, authentication, authorization, not_found, conflict, unavailable, timeout, dependency_failure and internal. HTTP status codes reflect the category while internal diagnostics remain in structured logs.

## Worker API Boundary
Worker endpoints are separate from browser administration operations and require worker authentication. Planned operations are registration, heartbeat, capability/resource report, job claim, job result and cancellation/status. The API never marks an unclaimed job successful.

## Idempotency
Mutating endpoints that can be retried should support idempotency keys or equivalent duplicate detection where side effects make retries unsafe.

## Observability
Requests carry a correlation identifier through API logs, task records, worker execution and audit events. Sensitive request fields are redacted.

## Deployment
The API is deployment-neutral. Reverse proxy, TLS and process management are deployment concerns. The same API application can run locally, in Docker, on a VPS or on Railway without changing business logic.
