"""Application lifecycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .bootstrap import Runtime
from .errors import classify_error
from .logging import get_logger
from .runtime_router import TelegramRuntimeRouter
from .telegram import TelegramAdapter


class ApplicationState(StrEnum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(slots=True)
class Application:
    runtime: Runtime
    telegram: TelegramAdapter
    router: TelegramRuntimeRouter
    state: ApplicationState = ApplicationState.CREATED

    async def start(self) -> None:
        if self.state is ApplicationState.RUNNING:
            return
        if self.state is ApplicationState.STARTING:
            return
        self.state = ApplicationState.STARTING
        try:
            await self.telegram.start()
            self.router.start()
            self.state = ApplicationState.RUNNING
            get_logger(__name__).info("application started")
        except Exception as exc:
            self.state = ApplicationState.FAILED
            safe = classify_error(exc)
            get_logger(__name__).error(
                "application startup failed",
                extra={"context": {"code": safe.code}},
            )
            raise

    async def stop(self) -> None:
        if self.state in {ApplicationState.STOPPED, ApplicationState.CREATED}:
            if self.state is ApplicationState.CREATED:
                self.runtime.database.engine.dispose()
                self.state = ApplicationState.STOPPED
            return
        self.state = ApplicationState.STOPPING
        try:
            await self.telegram.stop()
        finally:
            self.runtime.database.engine.dispose()
            self.state = ApplicationState.STOPPED


def create_application(runtime: Runtime) -> Application:
    telegram = TelegramAdapter(runtime.settings, runtime.services.events)
    router = TelegramRuntimeRouter(telegram, runtime.settings.owner_id)
    return Application(runtime=runtime, telegram=telegram, router=router)
