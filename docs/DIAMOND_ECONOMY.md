# Internal Diamond Economy

The Selfbot diamond system is an internal ledger. It is independent from Myoi and from `@MeowieeeQBot`.

## Safe defaults

| Policy | Default |
|---|---:|
| Minimum transfer | 1 |
| Maximum transfer | 1,000 |
| Daily sent amount | 3,000 |
| Transfer fee | 1% |
| Minimum fee | 1 |
| Maximum fee | 100 |
| Maximum single admin adjustment | 100,000 |

All limits are configuration values; no economic rule is hard-coded into Telegram handlers.

## User commands

- `.موجودی` or `/موجودی`
- `.انتقال <amount> <@username/ID>`
- `.انتقال <amount>` as a reply to the recipient
- `.تاریخچه` or `.تاریخچه_تراکنش`

The economy capability must be enabled for normal user operations. Self-transfer is rejected, negative balances are impossible, and the transfer plus fee is committed atomically.

## Admin commands

The current admin boundary is the configured application owner:

- `.افزایش الماس <amount> <@username/ID> [reason]`
- `.کاهش الماس <amount> <@username/ID> [reason]`

Admin changes are written to the same ledger and cannot create a negative wallet. A bounded maximum protects against accidental oversized adjustments.

## Data model

- `diamond_wallets`: one wallet per Telegram user ID.
- `diamond_transactions`: append-only transaction ledger containing sender, recipient, amount, fee, kind, actor and optional reason.

The database migration is `0004_diamond_economy`. PostgreSQL is the intended durable runtime database; SQLite remains suitable for temporary testing.

## Future earning sources

No earning rule is invented yet. Future rewards, purchases or other monetization sources must call the same wallet/ledger service rather than changing balances directly.
