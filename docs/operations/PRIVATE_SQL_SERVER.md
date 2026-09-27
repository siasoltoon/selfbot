# Private SQL Server Connectivity

This project supports an operator-hosted SQL Server without exposing SQL Server directly to the public internet.

## Architecture

```
GitHub-hosted Windows runner
        |
        | ephemeral Tailscale node
        v
      Tailnet
        |
        v
Operator laptop (Tailscale IP)
        |
        v
SQL Server
```

The application still uses `DATABASE_URL`; the private-network mechanism is infrastructure-only.

## GitHub/Tailscale setup

1. In Tailscale, create the tag `tag:selfbot-ci`.
2. Create a federated identity for GitHub Actions restricted to this repository.
3. Grant it the `auth_keys` scope and the `tag:selfbot-ci` identity.
4. In GitHub repository Settings → Secrets and variables → Actions:
   - secret `TS_OAUTH_CLIENT_ID`
   - secret `TS_AUDIENCE`
5. Add repository variable:
   - `TAILSCALE_ENABLED=true`
   - `SELFBOT_DATABASE_TAILSCALE_HOST=<laptop Tailscale hostname or 100.x.y.z>`

The workflow uses `tailscale/github-action@v4` and creates an ephemeral CI node. The node is removed after the workflow completes.

## Laptop setup

Install/sign in to Tailscale on the laptop and keep it connected while the database is required.

Configure SQL Server TCP/IP in SQL Server Configuration Manager. TCP/IP must be enabled and SQL Server restarted after network configuration changes.

Prefer a fixed SQL Server TCP port for this setup. Do not expose that port through the public router/firewall. Allow the port only on the private Tailscale interface as appropriate for the laptop firewall.

## Database URL

Set the GitHub Actions repository secret `DATABASE_URL` to the SQLAlchemy SQL Server URL using the laptop's Tailscale address, for example:

`mssql+pyodbc://USER:PASSWORD@100.x.y.z:PORT/selfbot?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no`

URL-encode reserved characters in the username/password.

## Validation order

1. Confirm the laptop is online in Tailscale.
2. Run the Telegram runtime workflow with `TAILSCALE_ENABLED=true`.
3. Confirm the Tailscale step can reach `SELFBOT_DATABASE_TAILSCALE_HOST`.
4. Let `alembic upgrade head` perform the real SQL Server migration.
5. Confirm the bot starts and database-dependent operations use the external database.
6. Perform a controlled restart and verify encrypted Telegram session reuse.

Do not mark SQL Server production verification PASS until the real migration and restart/session-reuse checks succeed.
