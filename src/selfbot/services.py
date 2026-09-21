"""Core service composition root."""
from __future__ import annotations
from dataclasses import dataclass
from .commands import CommandRegistry, PermissionChecker
from .db import Database
from .events import EventRouter
from .plugins import PluginManager, PluginPermissionChecker
from .scheduler import Scheduler
from .tasks import TaskManager
from .admin import AdminService
from .learning import LearningEngine
from .workflows import WorkflowEngine
from .reminders import ReminderService
from .security import SecurityService
from .backup import BackupService
from .analytics import Analytics
from .storage import StorageService
from .agents import AgentRouter
from .domain_store import DomainStore
from .hardening import StoragePolicy
@dataclass(slots=True)
class CoreServices:
    database:Database
    events:EventRouter
    commands:CommandRegistry
    tasks:TaskManager
    scheduler:Scheduler
    plugins:PluginManager
    domain_store:DomainStore
    learning:LearningEngine
    workflows:WorkflowEngine
    reminders:ReminderService
    security:SecurityService|None
    backup:BackupService
    analytics:Analytics
    storage:StorageService
    agents:AgentRouter
    storage_policy:StoragePolicy
    admin:AdminService|None
    @classmethod
    def create(cls,database:Database,*,permission_checker:PermissionChecker|None=None,plugin_permission_checker:PluginPermissionChecker|None=None,owner_id:str|None=None)->"CoreServices":
        events=EventRouter();tasks=TaskManager(database)
        security=SecurityService(owner_id) if owner_id else None
        admin=AdminService(owner_id) if owner_id else None
        return cls(database,events,CommandRegistry(permission_checker),tasks,Scheduler(tasks),PluginManager(permission_checker=plugin_permission_checker),DomainStore(database),LearningEngine(),WorkflowEngine(),ReminderService(),security,BackupService(),Analytics(),StorageService(),AgentRouter(),StoragePolicy(),admin)
