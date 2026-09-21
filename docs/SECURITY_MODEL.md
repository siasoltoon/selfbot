# Security Model

## Objectives
Protect Telegram sessions, API and worker credentials, personal data and AI memory, configuration, administrative operations, automation actions and backups. Sensitive controls fail closed.

## Trust Boundaries
1. Telegram and external event input
2. Core services
3. Plugin code
4. Administration API
5. PC Worker
6. External providers
7. Persistent storage
8. Backup and restore inputs

Data crossing a boundary is untrusted until validated.

## Identity and Permissions
Roles are Owner, Trusted User and unauthenticated/external caller. Authorization is enforced at command, plugin and task boundaries.

Owner-only operations include security configuration, credential changes, backup restore and emergency controls unless explicitly delegated by policy.

## Secrets
Secrets are supplied through environment/configuration: Telegram credentials/session, API keys, worker tokens and database credentials. Never commit, log or expose them in normal API responses. Redact sensitive values in errors.

## Telegram Session
Treat the Telegram session as a high-value credential. Keep it outside source control, protect filesystem access and never log it. Backup handling must be deliberate and protected.

## Input Validation
Validate Telegram event fields used by commands, API payloads, plugin manifests, task parameters, worker registration/results, backup metadata and external provider responses.

Never trust an external status or result field without validating schema and lifecycle state.

## Dangerous Actions
Sensitive automation and destructive operations require permission checks, parameter validation, safety policy and audit records. Emergency protection may disable dangerous automation/background work while preserving recovery and security controls.

## API Security
Administration APIs require authentication and authorization. Production deployments use TLS at the infrastructure boundary. Rate limiting and request-size controls are implementation-phase requirements.

## Worker Security
Worker endpoints require authentication and strict job validation. A worker cannot escalate capabilities by changing its own registration metadata.

## Backup Security
Backups may contain credentials or personal data. Treat them as sensitive artifacts, validate them before restore and protect access according to deployment needs.

## Auditability
Security-sensitive operations produce structured audit events containing actor, action, target, outcome, timestamp and correlation/task identifier. Avoid unnecessary sensitive payloads.

## Failure Policy
For security-sensitive operations: deny by default, fail closed, return a safe classified error, do not claim success and preserve recovery/security controls.
