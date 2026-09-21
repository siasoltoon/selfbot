# Architecture Map

## Current Phase
Phases 11-20 core capability implementation validated; runtime integration remains. Phase 4-10 remain in their documented integration/real-verification state.

## Implemented Foundation
- configuration, unified errors, persistence boundary, structured logging
- event router, command registry, durable task manager, scheduler
- plugin manifest/lifecycle/permission/dependency validation
- Telethon adapter boundary and application lifecycle
- Phase 4-10 capability boundaries
- Phase 11 admin service
- Phase 12 controlled learning
- Phase 13 workflow engine
- Phase 14 reminder service
- Phase 15 security service
- Phase 16 backup validation/export
- Phase 17 analytics aggregation
- Phase 18 smart storage metadata/search
- Phase 19 permission-gated agent router
- Phase 20 storage hardening policy

## Target Runtime Integration
Telegram Adapter
-> Event Router
-> CoreServices
-> capability services
-> Task Manager / Scheduler
-> optional PC Worker
-> external provider adapters
-> Persistence
-> Admin API/UI

The Phase 11-20 services currently remain deployment-neutral Python boundaries. Concrete HTTP/UI, database persistence, Telegram delivery, and provider adapters must be added behind replaceable infrastructure boundaries.

## Deployment
Deployment-neutral core supporting Railway, VPS, limited-runtime environments and personal PC/Laptop. No Phase 11-20 service embeds Railway-specific behavior.
