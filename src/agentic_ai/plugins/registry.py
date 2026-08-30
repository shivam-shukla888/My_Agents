"""
Plugin & Tool Registry Architecture.
Allows domain-specific plugins and connectors to dynamically register tools with the agent.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from langchain_core.tools import BaseTool


class BasePlugin(ABC):
    """
    Abstract base class for all work plugins.
    """

    def __init__(self, name: str, description: str, enabled: bool = True):
        self.name = name
        self.description = description
        self.enabled = enabled

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Return the list of LangChain tools provided by this plugin."""
        pass


class PluginRegistry:
    """
    Central registry for managing plugins, tool discovery, and dynamic tool injection.
    """

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        """Register a new plugin."""
        self._plugins[plugin.name] = plugin

    def unregister(self, plugin_name: str) -> None:
        """Remove a plugin from the registry."""
        self._plugins.pop(plugin_name, None)

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin by name."""
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = True
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin by name."""
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = False
            return True
        return False

    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """Return all registered plugins."""
        return dict(self._plugins)

    def get_active_tools(self) -> List[BaseTool]:
        """Return all active LangChain tools across enabled plugins."""
        tools: List[BaseTool] = []
        for plugin in self._plugins.values():
            if plugin.enabled:
                tools.extend(plugin.get_tools())
        return tools

    def get_summary(self) -> List[Dict[str, Any]]:
        """Diagnostic summary of plugins and their tool counts."""
        summary = []
        for name, plugin in self._plugins.items():
            tools = plugin.get_tools()
            summary.append({
                "plugin": name,
                "description": plugin.description,
                "enabled": plugin.enabled,
                "tool_count": len(tools),
                "tools": [t.name for t in tools],
            })
        return summary
