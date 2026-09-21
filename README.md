# Telegram Personal AI Operating System

A modular, secure and deployment-agnostic Telegram Personal AI Operating System.

## Status

Phase 0 bootstrap is complete and Phase 1 architecture design is in progress. Implementation proceeds incrementally from the engineering-memory state and is validated before each phase advances.

## Architecture

The system is designed around replaceable boundaries:

Telegram Client → Event Router → Core Engine → Plugins → Task Manager → Queue → Optional Workers → External Services

The core application remains deployment-agnostic. Railway, VPS, temporary/limited-runtime environments and personal PC/Laptop are deployment concerns, not business-logic dependencies.

## Development

Python 3.11+ is the baseline runtime for the foundation.

The repository intentionally keeps the initial foundation lightweight. Feature-specific dependencies are introduced only when their phase begins.

## Engineering State

Continuation state is maintained under [docs/engineering](docs/engineering/).

See [docs/MASTER_PROMPT.md](docs/MASTER_PROMPT.md) for the long-form product and architecture roadmap.
