# Architecture Map

## Current Implemented Foundation

```
Environment
    ↓
Configuration Loader
    ↓
Future Core Services
    ↓
Telegram / Plugins / Tasks / Queue / Optional Worker
```

Only the configuration boundary is implemented in the current bootstrap.

## Deployment Boundary
Core code must remain deployment-agnostic. Deployment-specific concerns belong in configuration, infrastructure, adapters and service definitions.

Supported targets:
- Railway
- Standard VPS
- Limited-runtime/temporary server
- Personal PC/Laptop

## Planned Modular Boundaries
- Telegram client adapter
- Event router
- Core services
- Database/storage
- Command registry
- Task manager
- Scheduler
- Plugin runtime
- Optional PC Worker protocol
- External service adapters
- Administration API/dashboard

No feature-specific implementation is claimed until its phase is completed and validated.
