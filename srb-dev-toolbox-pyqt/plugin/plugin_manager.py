from typing import Dict, Type, List, Optional, Callable
from .plugin_base import IPlugin, PluginInfo, PluginStatus


class PluginManager:
    _instance: Optional['PluginManager'] = None
    _plugins: Dict[str, Type[IPlugin]] = {}
    _instances: Dict[str, IPlugin] = {}
    _status_change_callbacks: List[Callable[[str, PluginStatus], None]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, plugin_class: Type[IPlugin]):
        plugin_id = plugin_class.get_id()
        cls._plugins[plugin_id] = plugin_class
        return plugin_class

    @classmethod
    def get_plugin(cls, plugin_id: str) -> Optional[Type[IPlugin]]:
        return cls._plugins.get(plugin_id)

    @classmethod
    def get_instance(cls, plugin_id: str) -> Optional[IPlugin]:
        if plugin_id in cls._instances:
            return cls._instances[plugin_id]
        
        plugin_class = cls.get_plugin(plugin_id)
        if plugin_class:
            instance = plugin_class()
            cls._instances[plugin_id] = instance
            return instance
        return None

    @classmethod
    def get_all_plugins(cls) -> Dict[str, Type[IPlugin]]:
        return cls._plugins.copy()

    @classmethod
    def get_all_plugin_infos(cls) -> List[PluginInfo]:
        return [p.get_info() for p in cls._plugins.values()]

    @classmethod
    def enable_plugin(cls, plugin_id: str) -> bool:
        instance = cls.get_instance(plugin_id)
        if instance:
            instance.enable()
            cls._notify_status_change(plugin_id, PluginStatus.ENABLED)
            return True
        return False

    @classmethod
    def disable_plugin(cls, plugin_id: str) -> bool:
        instance = cls.get_instance(plugin_id)
        if instance:
            instance.disable()
            cls._notify_status_change(plugin_id, PluginStatus.DISABLED)
            return True
        return False

    @classmethod
    def is_enabled(cls, plugin_id: str) -> bool:
        instance = cls._instances.get(plugin_id)
        if instance:
            return instance.is_enabled()
        plugin_class = cls._plugins.get(plugin_id)
        if plugin_class:
            return plugin_class.get_info().status == PluginStatus.ENABLED
        return False

    @classmethod
    def add_status_change_callback(cls, callback: Callable[[str, PluginStatus], None]):
        cls._status_change_callbacks.append(callback)

    @classmethod
    def remove_status_change_callback(cls, callback: Callable[[str, PluginStatus], None]):
        if callback in cls._status_change_callbacks:
            cls._status_change_callbacks.remove(callback)

    @classmethod
    def _notify_status_change(cls, plugin_id: str, status: PluginStatus):
        for callback in cls._status_change_callbacks:
            callback(plugin_id, status)

    @classmethod
    def get_enabled_plugins(cls) -> List[Type[IPlugin]]:
        return [
            p for p in cls._plugins.values()
            if cls.is_enabled(p.get_id())
        ]


def plugin(plugin_id: str, name: str, version: str = "1.0.0", 
           description: str = "", author: str = "", icon: str = "📦"):
    def decorator(cls):
        cls._info = PluginInfo(
            plugin_id=plugin_id,
            name=name,
            version=version,
            description=description,
            author=author,
            icon=icon,
            status=PluginStatus.ENABLED
        )
        PluginManager.register(cls)
        return cls
    return decorator
