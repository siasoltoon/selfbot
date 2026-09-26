# Telegram Global Capability Panel

The linked Telegram user account opens the panel with `/panel` or `/پنل`.

## Where it works

- Saved Messages
- private chats
- groups/supergroups where the account can send messages

The command is handled from the linked user account's outgoing messages. The interactive panel is delivered through the onboarding bot's Telegram Inline Mode, so the panel can be inserted into the same chat.

## One-time Telegram setup

Enable Inline Mode for the onboarding bot in BotFather with `/setinline`.

## Security

Panel tokens contain no secret material. They are authenticated with a signature derived from the existing Telegram session-encryption secret. The onboarding bot verifies both the token and the callback sender before changing a capability.

Capability state is persisted per onboarding owner in the existing durable `domain_state` table.

Security and task/scheduler controls are core protections and remain enabled; they are shown in the panel without a disable action.

## Capability semantics

The panel changes durable capability state; it is not a cosmetic list. Gated feature code must call `CapabilityService.require(owner_id, capability_id)` before executing a capability.

Enabled state is separate from dependency availability. If an AI, voice, OCR, web or PC Worker dependency is unavailable, the application must fail safely rather than fabricate a successful result.

## Professional Control Center v2

The panel is hierarchical rather than a flat ON/OFF list:

- Main menu with module categories and aggregate status.
- Category pages for AI/Agents, Memory, Voice/Media, Web Intelligence, OCR/Documents, Automation/Tasks, Plugins, PC Worker, Data/Backup, Analytics/Learning, Security, and Account/System.
- Module pages expose descriptions, durable state, and nested sub-capabilities.
- Parent capability changes cascade safely to child capability state.
- Security and Task/Scheduler core protections remain non-disableable.
- Account/System exposes the connected Telegram account and links back to capability/security status.

The panel is still a control surface, not a claim that every provider-backed domain is production-connected. A feature is considered operational only after its domain service is wired through CapabilityService.require() and its real provider/deployment verification passes.
