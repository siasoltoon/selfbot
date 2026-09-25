"""Application lifecycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .bootstrap import Runtime
from .errors import classify_error
from .logging import get_logger
from .runtime_router import TelegramRuntimeRouter
from .telegram import TelegramAdapter
from .multi_user_security import SessionCipher
from .multi_user_telegram import MultiUserTelegramRuntime, OnboardingBot, TelegramAuthenticationService, TelegramSessionStore


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
    telegram: TelegramAdapter | MultiUserTelegramRuntime
    router: TelegramRuntimeRouter
    onboarding: OnboardingBot | None = None
    state: ApplicationState = ApplicationState.CREATED

    async def start(self) -> None:
        if self.state is ApplicationState.RUNNING:
            return
        if self.state is ApplicationState.STARTING:
            return
        self.state = ApplicationState.STARTING
        try:
            if self.onboarding is not None:
                await self.onboarding.start()
                await self.telegram.start(self.runtime.settings.telegram_api_id or "", self.runtime.settings.telegram_api_hash or "")
            else:
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
            if self.onboarding is not None:
                await self.telegram.stop()
                await self.onboarding.stop()
            else:
                await self.telegram.stop()
        finally:
            self.runtime.database.engine.dispose()
            self.state = ApplicationState.STOPPED


def create_application(runtime: Runtime) -> Application:
    if runtime.settings.telegram_onboarding_bot_token and runtime.settings.telegram_session_encryption_key:
        if not runtime.settings.telegram_api_id or not runtime.settings.telegram_api_hash:
            raise ValueError("Telegram API credentials are required for multi-user mode")
        store = TelegramSessionStore(runtime.database, SessionCipher(runtime.settings.telegram_session_encryption_key))
        auth = TelegramAuthenticationService(runtime.settings.telegram_api_id, runtime.settings.telegram_api_hash, store)
        telegram = MultiUserTelegramRuntime(store, runtime.services.events)
        onboarding = OnboardingBot(runtime.settings.telegram_onboarding_bot_token, runtime.settings.telegram_api_id, runtime.settings.telegram_api_hash, auth, store)
        router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True)
        return Application(runtime=runtime, telegram=telegram, router=router, onboarding=onboarding)
    telegram = TelegramAdapter(runtime.settings, runtime.services.events)
    router = TelegramRuntimeRouter(telegram, runtime.settings.owner_id)
    return Application(runtime=runtime, telegram=telegram, router=router)
