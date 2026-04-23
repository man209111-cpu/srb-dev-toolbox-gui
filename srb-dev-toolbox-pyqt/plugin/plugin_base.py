from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class PluginStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"


@dataclass
class PluginInfo:
    plugin_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    icon: str = "📦"
    status: PluginStatus = PluginStatus.DISABLED
    metadata: Dict[str, Any] = field(default_factory=dict)


class IPlugin:
    _info: PluginInfo

    @classmethod
    def get_info(cls) -> PluginInfo:
        return cls._info

    @classmethod
    def get_id(cls) -> str:
        return cls._info.plugin_id

    @classmethod
    def get_name(cls) -> str:
        return cls._info.name

    def enable(self):
        self._info.status = PluginStatus.ENABLED

    def disable(self):
        self._info.status = PluginStatus.DISABLED

    def is_enabled(self) -> bool:
        return self._info.status == PluginStatus.ENABLED

    def create_widget(self, parent=None):
        raise NotImplementedError("子类必须实现 create_widget 方法")
