# Architecture Map

## Current Phase
Phase 2 core foundation.

## Implemented
- configuration and unified errors
- SQLAlchemy/Alembic persistence
- structured logging
- runtime bootstrap
- event router
- command registry
- durable task manager
- scheduler
- plugin lifecycle manager
- CoreServices composition
- automated CI

## Next Boundary
Application Runtime
-> Telegram Adapter
-> CoreServices
-> graceful startup/shutdown

Telegram library objects remain inside the adapter layer.

## Deployment
Deployment-neutral core supporting Railway, VPS, temporary/limited-runtime environments and personal PC/Laptop. Provider-specific behavior remains in infrastructure/configuration.
