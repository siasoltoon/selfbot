"""Database engine/session foundation."""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for application ORM models."""


@contextmanager
def connect_with_retries(
    engine: Engine,
    *,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> Generator[Connection, None, None]:
    """Acquire one DB connection with bounded pre-work retries.

    Only connection acquisition is retried. Once a connection has been
    yielded, exceptions from the caller are never replayed.
    """

    if retries < 0:
        raise ValueError("retries must be non-negative")
    if retry_delay < 0:
        raise ValueError("retry_delay must be non-negative")

    connection: Connection | None = None
    for attempt in range(retries + 1):
        try:
            connection = engine.connect()
            break
        except DBAPIError:
            if attempt >= retries:
                raise
            engine.dispose()
            if retry_delay:
                time.sleep(retry_delay * (2**attempt))

    if connection is None:  # pragma: no cover - defensive guard
        raise RuntimeError("database connection was not acquired")

    try:
        yield connection
    finally:
        connection.close()


class Database:
    """Owns the SQLAlchemy engine and session factory.

    Network-backed databases can briefly disappear (for example while a
    deployment tunnel reconnects). Retries are limited to initial connection
    checkout so application writes are never replayed automatically.
    """

    def __init__(
        self,
        url: str,
        *,
        echo: bool = False,
        connect_retries: int = 3,
        connect_retry_delay: float = 1.0,
    ) -> None:
        if not url.strip():
            raise ValueError("database URL must not be empty")
        if connect_retries < 0:
            raise ValueError("connect_retries must be non-negative")
        if connect_retry_delay < 0:
            raise ValueError("connect_retry_delay must be non-negative")

        connect_args: dict[str, Any] = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        elif url.startswith("mssql+pyodbc"):
            connect_args["timeout"] = 10
        elif url.startswith(("postgresql://", "postgresql+")):
            connect_args["connect_timeout"] = 15

        engine_kwargs: dict[str, Any] = {
            "echo": echo,
            "pool_pre_ping": True,
            "connect_args": connect_args,
        }
        if not url.startswith("sqlite"):
            engine_kwargs["pool_recycle"] = 300
            engine_kwargs["pool_timeout"] = 30

        self.engine: Engine = create_engine(url, **engine_kwargs)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self.connect_retries = connect_retries
        self.connect_retry_delay = connect_retry_delay

    def _acquire_connection(self, session: Session) -> Session:
        """Force pool checkout before caller executes work."""
        for attempt in range(self.connect_retries + 1):
            try:
                session.connection()
                return session
            except DBAPIError:
                session.close()
                if attempt >= self.connect_retries:
                    raise
                self.engine.dispose()
                if self.connect_retry_delay:
                    time.sleep(self.connect_retry_delay * (2**attempt))
                session = self.session_factory()

        return session

    def ping(self) -> bool:
        for attempt in range(self.connect_retries + 1):
            try:
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                return True
            except DBAPIError:
                if attempt >= self.connect_retries:
                    raise
                self.engine.dispose()
                if self.connect_retry_delay:
                    time.sleep(self.connect_retry_delay * (2**attempt))
        return False

    @contextmanager
    def session(self, *, read_only: bool = False) -> Generator[Session, None, None]:
        """Provide a session with explicit transaction semantics.

        Read-only callers roll back the implicit transaction opened by a SELECT
        instead of issuing a network COMMIT. This avoids turning a harmless
        connectivity interruption into a failed read operation while keeping
        normal write callers transactional.
        """
        session = self.session_factory()
        try:
            session = self._acquire_connection(session)
            yield session
            if read_only:
                session.rollback()
            else:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_schema_for_tests(self) -> None:
        """Create ORM metadata for isolated tests.

        Production schema changes must use Alembic migrations.
        """

        Base.metadata.create_all(self.engine)
