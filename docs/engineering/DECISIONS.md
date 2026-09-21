# Engineering Decisions

## 2026-09-21 — Python foundation
Decision: use Python 3.11+ as the baseline runtime for the initial application foundation.

Reason:
- appropriate for Telegram automation and service-oriented application code
- keeps the bootstrap dependency-light
- supports incremental introduction of feature-specific dependencies

## 2026-09-21 — Deployment neutrality
Decision: deployment targets are infrastructure/configuration concerns, not core business-logic branches.

Reason:
The same application must remain portable across Railway, VPS, limited-runtime environments and personal PC/Laptop.

## 2026-09-21 — Optional worker boundary
Decision: PC Worker integration is optional infrastructure and is represented in configuration without making worker availability a core startup dependency.

Reason:
Lightweight application functionality must continue when the worker is offline.

## 2026-09-21 — Engineering memory is authoritative
Decision: continuation state is stored under docs/engineering and updated after meaningful validated work.

Reason:
New conversations must resume from exact validated state without repeating repository-wide investigation.
