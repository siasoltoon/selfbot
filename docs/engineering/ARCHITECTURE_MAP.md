# Architecture Map

Telegram Adapter
-> Event Router
-> Core Services
-> Domain Capability Services
-> Task Manager / Scheduler
-> Persistence
-> optional Worker / external providers

Admin/API/UI, Telegram, AI, voice, web, OCR and worker transports remain adapters around provider-neutral core contracts.

## New Integration Boundaries
- DomainStore + SQLAlchemy models for durable domain state.
- Alembic migrations for schema evolution.
- OCRBenchmark for measured OCR evaluation.
- AdversarialHarness for explicit failure testing.
- UXValidator for Persian/English Telegram response constraints.
- ReleaseAudit for production evidence tracking.

## Deployment Rule
Core logic remains deployment-neutral. Railway/VPS/personal-PC behavior belongs in environment configuration and infrastructure adapters.

## Deployment Runtime
- `scripts/run_bot.py` is the shared process entrypoint.
- `.github/workflows/telegram-runtime.yml` is a deployment adapter for GitHub-hosted Windows runners.
- Core application logic remains deployment-agnostic.

## Multi-user Telegram path
Installation Bot → Authentication Service → encrypted Session Store → Multi-user Telegram Runtime → Event Router → Core Services.

The installation bot is a normal Telegram bot account. Each connected user's selfbot account is an independent Telethon client. Persistent account sessions are encrypted at rest; transient login code/2FA input is not persisted or dispatched to the core event bus.

## Telegram authentication path — current
Installation Bot → QR Authentication Service → transient QR challenge → optional transient 2FA → encrypted Session Store → Multi-user Telegram Runtime → Event Router.

The production onboarding bot does not collect Telegram login codes in chat. QR tokens are rendered as short-lived PNG media, the QR wait runs concurrently before scanning, and QR media/transient client state is cleaned up after completion, expiry, cancellation, or failure.

### QR/2FA lifecycle rule
- QR challenge lifetime is short and is controlled by Telethon's QR expiry.
- Once Telegram accepts the QR and requests 2FA, the transient authenticated client must receive a separate post-scan lifetime window.
- The current implementation extends the pending session's cleanup deadline to the configured authentication-service TTL at the 2FA boundary.
- This prevents the QR token's expiry from disconnecting the client while the user enters the 2FA password.
- A future cleanup may split `qr_expires_at` and `two_fa_expires_at` into distinct fields if additional lifecycle states require it.

### Post-auth persistence safety
- Production QR clients use Telethon `StringSession()` from the beginning so successful authentication can yield a durable session string.
- Durable session persistence is part of the authentication transaction boundary: a successful Telegram authentication is not reported as an application-level success until the encrypted session is stored.
- If persistence fails after authentication, the transient authenticated client attempts `log_out()` before disconnecting, preventing an unmanaged authenticated session from being retained.

## Global Telegram Capability Panel
Linked user account outgoing message
-> EventEnvelope (telegram.new_message, outgoing=true)
-> TelegramRuntimeRouter
-> MultiUserTelegramRuntime.open_panel()
-> onboarding bot InlineQuery
-> signed panel token verification
-> CapabilityService / DomainStore
-> inline callback
-> owner verification
-> durable capability toggle

The linked-account runtime deliberately ignores incoming group commands for control operations. This prevents other group members from controlling the owner's selfbot. The onboarding bot owns inline callbacks because Telegram/Telethon callback buttons are bot-side interactions; the linked user account only requests and sends the inline result into the target chat.

Capability state is persisted per onboarding owner in the existing domain_state table, avoiding a duplicate settings database. Security and task/scheduler are core protections and are not user-disableable.


## Telegram Panel v2
- Linked user emits /panel or /پنل.
- Runtime performs signed inline query against onboarding bot.
- Onboarding bot renders hierarchical PanelService pages and handles authenticated callback navigation.
- PanelService owns transport-neutral category/navigation metadata; CapabilityService owns durable owner-scoped state and parent/child gate semantics.


## Internal Diamond Economy
Telegram event -> RuntimeRouter -> EconomyService -> DiamondWallet/DiamondTransaction -> configured database.
- EconomyService is independent of Myoi and accepts canonical user IDs.
- Telegram adapter resolves @username and reply recipients before calling the core.
- User operations are capability-gated in the Selfbot owner scope.
- Admin adjustments are owner-authorized and ledger-recorded.
- Balance changes are performed together with the ledger entry inside one database session.


## Real Panel Execution
Telegram event -> RuntimeRouter -> CapabilityService gate -> concrete core operation -> Telegram response.
- Panel state remains durable and owner-scoped.
- Capability child enablement now activates its parent module so UI actions are effective.

## Myoi Adapter
Linked Telethon user client -> MyoiTelegramAdapter -> @MeowieeeQBot messages/visible inline buttons.
- Adapter is intentionally transport-focused and does not hardcode undocumented callback data.
- Workflow services will consume this adapter after real observations establish stable labels/flows.


## 2026-09-27 — External Database Persistence
- Storage adapter boundary: SQLAlchemy `Database` accepts SQLite, PostgreSQL and SQL Server (`mssql+pyodbc`) without changing core services.
- Durable schema ownership: Alembic imports all ORM models; migration `0003_durable_runtime_state` provisions domain state, security audit, encrypted Telegram sessions and diamond economy.


## 2026-09-27 — Private DB transport
- GitHub-hosted runtime may reach operator-hosted SQL Server through an ephemeral Tailscale CI node.
- Tailscale is an infrastructure adapter; core services continue to consume only deployment-neutral `DATABASE_URL`.
- SQL Server remains private and is not made publicly reachable by the application.
