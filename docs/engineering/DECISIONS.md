# Engineering Decisions

## 2026-09-21 — Python foundation
Decision: use Python 3.11+ as the baseline runtime for the application foundation.
Reason: suitable for Telegram automation/service code while keeping the bootstrap dependency-light.

## 2026-09-21 — Deployment neutrality
Decision: deployment targets are infrastructure/configuration concerns, not core business-logic branches.
Reason: the same application must remain portable across Railway, VPS, limited-runtime environments and personal PC/Laptop.

## 2026-09-21 — Optional worker boundary
Decision: PC Worker integration is optional infrastructure and is not a core startup dependency.
Reason: lightweight functionality must continue when the worker is offline.

## 2026-09-21 — Engineering memory is authoritative
Decision: continuation state lives under docs/engineering and is updated after meaningful validated work.
Reason: new conversations must resume from exact state.

## 2026-09-21 — MIT license
Decision: repository is released under the MIT License.
Reason: permissive licensing matches the intended reusable/open development model.
