"""Core service composition root."""

from __future__ import annotations

from dataclasses import dataclass

from .commands import CommandRegistry, PermissionChecker
from .db import Database
from .events import EventRouter
from .plugins import PluginManager, PluginPermissionChecker
from .scheduler import Scheduler
from .tasks import TaskManager


@dataclass(slots=True)
class CoreServices:
    database: Database
    events: EventRouter
    commands: CommandRegistry
    tasks: TaskManager
    scheduler: Scheduler
    plugins: PluginManager

    @classmethod
    def create(
        cls,
        database: Database,
        *,
        permission_checker: PermissionChecker | None = None,
        plugin_permission_checker: PluginPermissionChecker | None = None,
    ) -> "CoreServices":
        events = EventRouter()
        tasks = TaskManager(database)
        return cls(
            database=database,
            events=events,
            commands=CommandRegistry(permission_checker),
            tasks=tasks,
            scheduler=Scheduler(tasks),
            plugins=PluginManager(
                permission_checker=plugin_permission_checker,
            ),
        )
