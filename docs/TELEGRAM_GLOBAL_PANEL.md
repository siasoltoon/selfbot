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