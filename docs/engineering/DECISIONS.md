# Engineering Decisions

- Python 3.11+ baseline.
- SQLAlchemy 2.x + Alembic for persistence/migrations.
- SQLite default local database; PostgreSQL supported through configuration.
- Telethon confined to Telegram adapter.
- PC Worker is optional and must report explicit availability.
- Provider-neutral AI/voice/web/OCR contracts; missing providers never produce fake success.
- Controlled learning is approval-gated.
- Backup payloads use deterministic checksums before restore acceptance.
- Phase 21 metrics are measured only from supplied labeled cases; no synthetic score is presented as real performance.
- Phase 22 failures are explicit outcomes; the harness never converts an exception into a claimed correct answer.
- Phase 23 Persian UX requires explicit RTL metadata.
- Phase 24/25 release status is evidence-driven; NOT_RUN/BLOCKED evidence prevents final release pass.
