# PC Worker Architecture

## Role
The PC Worker is optional infrastructure for CPU/GPU-heavy jobs. It is not a required dependency for the core application. Potential workloads include local AI inference, speech processing, TTS, media processing, large downloads and data/ML processing.

## Protocol Boundary
Core -> authenticated HTTPS -> Worker API -> Worker Runtime

Transport is an adapter boundary. Core job semantics do not depend on a particular HTTP framework.

## Lifecycle
REGISTER -> AUTHENTICATE -> HEARTBEAT -> AVAILABLE -> CLAIM -> EXECUTE -> REPORT RESULT

A worker becomes unavailable after a configurable heartbeat timeout. Offline state is explicit.

## Authentication
Workers authenticate using a secret token supplied through deployment configuration. Tokens are never hardcoded or logged. Invalid credentials are rejected. Credentials are rotated through configuration.

## Capabilities
Registration includes supported job types, CPU/GPU availability, resource limits and protocol version. The core dispatches only compatible jobs.

## Durable Job States
queued, claimed, running, succeeded, failed, cancelled, timed_out, deferred, worker_offline.

A job cannot become succeeded merely because dispatch was requested.

## Heartbeat and Recovery
Heartbeat contains worker ID, timestamp, capabilities, resource summary and protocol version. Missed heartbeats cause the core to mark the worker offline and recover assigned jobs according to retry/defer policy.

## Retry, Timeout and Cancellation
Each job defines timeout, retry count, retry/backoff policy and cancellation policy. Retries must account for idempotency. Cancellation is cooperative where possible and final state distinguishes requested, completed and failed cancellation.

## Safety Rule
If no worker executed a job, the system reports deferred/offline/failure rather than fabricated completion.

## Deployment Independence
The worker may run on a personal PC/Laptop, VPS or temporary server. The core does not assume a fixed network topology or cloud provider.
