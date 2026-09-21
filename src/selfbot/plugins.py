"""Plugin manifest, validation and lifecycle boundary."""
from __future__ import annotations
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol
from .errors import ConflictError, DependencyError, ValidationError

class PluginState(StrEnum):
    REGISTERED="registered"; ENABLED="enabled"; DISABLED="disabled"; FAILED="failed"

class PluginPermissionChecker(Protocol):
    def check(self, plugin_id:str, permission:str)->bool|Awaitable[bool]: ...

class PluginLifecycle(Protocol):
    def start(self)->Any: ...
    def stop(self)->Any: ...

@dataclass(frozen=True,slots=True)
class PluginManifest:
    plugin_id:str
    version:str
    api_version:str
    dependencies:tuple[str,...]=()
    permissions:tuple[str,...]=()
    capabilities:tuple[str,...]=()
    config_schema:dict[str,Any]=field(default_factory=dict)
    description:str=""
    def __post_init__(self)->None:
        if not self.plugin_id.strip() or not self.version.strip() or not self.api_version.strip():
            raise ValidationError("plugin_id, version and api_version must not be empty")
        if len(set(self.dependencies))!=len(self.dependencies): raise ValidationError("plugin dependencies must be unique")
        if len(set(self.permissions))!=len(self.permissions): raise ValidationError("plugin permissions must be unique")
        if len(set(self.capabilities))!=len(self.capabilities): raise ValidationError("plugin capabilities must be unique")

@dataclass(slots=True)
class PluginRegistration:
    manifest:PluginManifest
    factory:Callable[[],PluginLifecycle]
    state:PluginState=PluginState.REGISTERED
    instance:PluginLifecycle|None=None
    config:dict[str,Any]=field(default_factory=dict)

class PluginManager:
    def __init__(self,*,api_version:str="1",permission_checker:PluginPermissionChecker|None=None)->None:
        self.api_version=api_version; self.permission_checker=permission_checker; self._plugins:dict[str,PluginRegistration]={}
    def register(self,manifest:PluginManifest,factory:Callable[[],PluginLifecycle])->None:
        if manifest.plugin_id in self._plugins: raise ConflictError(f"plugin already registered: {manifest.plugin_id}")
        if manifest.api_version!=self.api_version: raise ValidationError(f"plugin API version {manifest.api_version} is incompatible")
        self._plugins[manifest.plugin_id]=PluginRegistration(manifest,factory)
        self._validate_dependency_graph()
    def _validate_dependency_graph(self)->None:
        graph={k:set(v.manifest.dependencies) for k,v in self._plugins.items()}
        visiting:set[str]=set(); visited:set[str]=set()
        def visit(node:str)->None:
            if node in visiting: raise DependencyError("circular plugin dependency detected",retryable=False)
            if node in visited:return
            visiting.add(node)
            for dep in graph[node]:visit(dep)
            visiting.remove(node);visited.add(node)
        for node in graph:visit(node)
    def get(self,plugin_id:str)->PluginRegistration:
        try:return self._plugins[plugin_id]
        except KeyError as exc:raise ValidationError(f"plugin not registered: {plugin_id}") from exc
    def list(self)->tuple[PluginRegistration,...]:return tuple(self._plugins.values())
    def configure(self,plugin_id:str,values:dict[str,Any])->None:
        reg=self.get(plugin_id)
        if not isinstance(values,dict):raise ValidationError("plugin config must be an object")
        unknown=set(values)-set(reg.manifest.config_schema)
        if unknown:raise ValidationError(f"unknown plugin config keys: {','.join(sorted(unknown))}")
        reg.config=dict(values)
    async def enable(self,plugin_id:str)->None:
        reg=self.get(plugin_id)
        if reg.state is PluginState.ENABLED:return
        for dependency in reg.manifest.dependencies:
            if self.get(dependency).state is not PluginState.ENABLED:raise DependencyError(f"plugin dependency is not enabled: {dependency}",retryable=False)
        if reg.manifest.permissions:
            if self.permission_checker is None:raise ValidationError("plugin permission checker is not configured")
            for permission in reg.manifest.permissions:
                allowed=self.permission_checker.check(plugin_id,permission)
                if inspect.isawaitable(allowed):allowed=await allowed
                if not allowed:raise ValidationError(f"plugin permission denied: {permission}")
        try:
            instance=reg.factory(); result=instance.start()
            if inspect.isawaitable(result):await result
            reg.instance=instance;reg.state=PluginState.ENABLED
        except Exception:
            reg.instance=None;reg.state=PluginState.FAILED;raise
    async def disable(self,plugin_id:str)->None:
        reg=self.get(plugin_id)
        if reg.state is not PluginState.ENABLED:reg.state=PluginState.DISABLED;return
        if reg.instance is None:reg.state=PluginState.FAILED;raise ValidationError("enabled plugin has no runtime instance")
        try:
            result=reg.instance.stop()
            if inspect.isawaitable(result):await result
            reg.instance=None;reg.state=PluginState.DISABLED
        except Exception:
            reg.state=PluginState.FAILED;raise
