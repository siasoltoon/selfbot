# Architecture Map

## Current Phase
Phase 2 core foundation.

## Implemented
- configuration
- unified errors
- SQLAlchemy/Alembic persistence boundary
- structured logging
- runtime bootstrap
- normalized event router
- command registry
- durable task manager
- scheduler primitives
- automated CI

## Next Implementation Boundary
Core Service Container
-> Event Router
-> Command Registry
-> Task Manager
-> Scheduler
-> Plugin Runtime

Plugin Runtime remains behind the documented manifest/lifecycle/permission interfaces.

## Deployment
Deployment-neutral core supporting Railway, VPS, temporary/limited-runtime environments and personal PC/Laptop. Provider-specific behavior remains in infrastructure/configuration.
