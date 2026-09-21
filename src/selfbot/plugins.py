"""Plugin manifest and lifecycle boundary."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

from .errors import ConflictError, DependencyError, ValidationError


class PluginState(StrEnum):
    REGISTERED = "registered"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"


class PluginPermissionChecker(Protocol):
    def check(self, plugin_id: str, permission: str) -> bool | Awaitable[bool]:
        """Return whether a plugin may use the named capability."""


class PluginLifecycle(Protocol):
    def start(self) -> Any:
        """Initialize the plugin."""

    def stop(self) -> Any:
        """Stop the plugin safely."""


@dataclass(frozen=True, slots=True)
class PluginManifest:
    plugin_id: str
    version: str
    api_version: str
    dependencies: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        if not self.plugin_id.strip():
            raise ValidationError("plugin_id must not be empty")
        if not self.version.strip():
            raise ValidationError("plugin version must not be empty")
        if not self.api_version.strip():
            raise ValidationError("plugin api_version must not be empty")
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValidationError("plugin dependencies must be unique")
        if len(set(self.permissions)) != len(self.permissions):
            raise ValidationError("plugin permissions must be unique")


@dataclass(slots=True)
class PluginRegistration:
    manifest: PluginManifest
    factory: Callable[[], PluginLifecycle]
    state: PluginState = PluginState.REGISTERED
    instance: PluginLifecycle | None = None


class PluginManager:
    """Validates plugin metadata and controls lifecycle transitions."""

    def __init__(
        self,
        *,
        api_version: str = "1",
        permission_checker: PluginPermissionChecker | None = None,
    ) -> None:
        self.api_version = api_version
        self.permission_checker = permission_checker
        self._plugins: dict[str, PluginRegistration] = {}

    def register(
        self,
        manifest: PluginManifest,
        factory: Callable[[], PluginLifecycle],
    ) -> None:
        if manifest.plugin_id in self._plugins:
            raise ConflictError(f"plugin already registered: {manifest.plugin_id}")
        if manifest.api_version != self.api_version:
            raise ValidationError(
                f"plugin API version {manifest.api_version} is incompatible"
            )
        self._plugins[manifest.plugin_id] = PluginRegistration(
            manifest=manifest,
            factory=factory,
        )

    def get(self, plugin_id: str) -> PluginRegistration:
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise ValidationError(f"plugin not registered: {plugin_id}") from exc

    def list(self) -> tuple[PluginRegistration, ...]:
        return tuple(self._plugins.values())

    async def enable(self, plugin_id: str) -> None:
        registration = self.get(plugin_id)
        if registration.state is PluginState.ENABLED:
            return

        for dependency in registration.manifest.dependencies:
            dependency_registration = self.get(dependency)
            if dependency_registration.state is not PluginState.ENABLED:
                raise DependencyError(
                    f"plugin dependency is not enabled: {dependency}",
                    retryable=False,
                )

        if registration.manifest.permissions:
            if self.permission_checker is None:
                raise ValidationError("plugin permission checker is not configured")
            for permission in registration.manifest.permissions:
                allowed = self.permission_checker.check(
                    registration.manifest.plugin_id,
                    permission,
                )
                if inspect.isawaitable(allowed):
                    allowed = await allowed
                if not allowed:
                    raise ValidationError(
                        f"plugin permission denied: {permission}"
                    )

        try:
            instance = registration.factory()
            result = instance.start()
            if inspect.isawaitable(result):
                await result
            registration.instance = instance
            registration.state = PluginState.ENABLED
        except Exception:
            registration.state = PluginState.FAILED
            registration.instance = None
            raise

    async def disable(self, plugin_id: str) -> None:
        registration = self.get(plugin_id)
        if registration.state is not PluginState.ENABLED:
            registration.state = PluginState.DISABLED
            return

        if registration.instance is None:
            registration.state = PluginState.FAILED
            raise ValidationError("enabled plugin has no runtime instance")

        try:
            result = registration.instance.stop()
            if inspect.isawaitable(result):
                await result
            registration.instance = None
            registration.state = PluginState.DISABLED
        except Exception:
            registration.state = PluginState.FAILED
            raise
