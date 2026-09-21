import asyncio

import pytest

from selfbot.errors import DependencyError, ValidationError
from selfbot.plugins import PluginManager, PluginManifest, PluginState


class Checker:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def check(self, plugin_id, permission):
        return self.allowed


class DemoPlugin:
    def __init__(self):
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


def test_plugin_lifecycle():
    instance = DemoPlugin()
    manager = PluginManager(permission_checker=Checker())

    manager.register(
        PluginManifest(
            plugin_id="demo",
            version="1.0.0",
            api_version="1",
            permissions=("send_message",),
        ),
        lambda: instance,
    )

    asyncio.run(manager.enable("demo"))
    assert manager.get("demo").state is PluginState.ENABLED
    assert instance.started is True

    asyncio.run(manager.disable("demo"))
    assert manager.get("demo").state is PluginState.DISABLED
    assert instance.stopped is True


def test_plugin_dependency_must_be_enabled():
    manager = PluginManager()
    manager.register(
        PluginManifest(plugin_id="dependent", version="1", api_version="1", dependencies=("base",)),
        DemoPlugin,
    )
    manager.register(
        PluginManifest(plugin_id="base", version="1", api_version="1"),
        DemoPlugin,
    )

    with pytest.raises(DependencyError):
        asyncio.run(manager.enable("dependent"))


def test_plugin_permission_is_required():
    manager = PluginManager(permission_checker=Checker(False))
    manager.register(
        PluginManifest(
            plugin_id="restricted",
            version="1",
            api_version="1",
            permissions=("dangerous_action",),
        ),
        DemoPlugin,
    )

    with pytest.raises(ValidationError):
        asyncio.run(manager.enable("restricted"))


def test_plugin_api_version_is_validated():
    manager = PluginManager(api_version="2")

    with pytest.raises(ValidationError):
        manager.register(
            PluginManifest(plugin_id="old", version="1", api_version="1"),
            DemoPlugin,
        )


def test_plugin_config_and_capabilities():
    manager = PluginManager()
    manager.register(
        PluginManifest(plugin_id="cfg", version="1", api_version="1",
                       capabilities=("utility",), config_schema={"enabled": True}),
        DemoPlugin,
    )
    manager.configure("cfg", {"enabled": False})
    assert manager.get("cfg").config == {"enabled": False}

def test_plugin_circular_dependency_rejected():
    manager = PluginManager()
    manager.register(PluginManifest(plugin_id="a", version="1", api_version="1", dependencies=("b",)), DemoPlugin)
    with pytest.raises(DependencyError):
        manager.register(PluginManifest(plugin_id="b", version="1", api_version="1", dependencies=("a",)), DemoPlugin)
