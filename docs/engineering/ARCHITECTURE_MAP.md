# Architecture Map

## Current Phase
Phase 10 — Advanced PC Worker, with Phase 4-10 core capability layers implemented and awaiting full runtime integration.

## Implemented
- configuration, unified errors, persistence boundary, structured logging
- event router, command registry, durable task manager, scheduler
- plugin manifest/lifecycle/permission/dependency validation
- Telethon adapter boundary and application lifecycle
- Telegram self-management service boundary
- automation/content engine
- isolated game/economy primitives
- provider-neutral AI/memory services
- safe web retrieval boundary
- STT/TTS provider contracts
- authenticated PC Worker registry/runtime primitives

## Runtime Integration Target
Telegram Adapter
-> Event Router
-> CoreServices
-> capability services
-> Task Manager
-> optional PC Worker
-> external provider adapters
-> Persistence

Telegram/library/provider/worker transport objects remain behind adapters.

## Deployment
Deployment-neutral core supporting Railway, VPS, temporary/limited-runtime environments and personal PC/Laptop. Provider-specific behavior remains in infrastructure/configuration.
