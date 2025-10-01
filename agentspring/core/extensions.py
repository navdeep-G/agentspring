"""
Extension registry for managing plugins and extensions.

This module provides the ExtensionRegistry class which is responsible for
registering and managing plugins and their extensions.
"""
from typing import Dict, List, Type, Any, Optional, TypeVar, Generic, Set
from collections import defaultdict

from .base import Plugin, ExtensionPoint, Agent, Tool, Workflow
from .exceptions import (
    PluginError,
    DependencyError,
    RegistrationError,
    ExtensionError
)

T = TypeVar('T', bound=ExtensionPoint)

class ExtensionRegistry:
    """Registry for managing plugins and their extensions."""
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._extensions: Dict[Type[ExtensionPoint], List[Any]] = defaultdict(list)
        self._extension_map: Dict[Type[ExtensionPoint], Dict[str, Any]] = defaultdict(dict)
        self._initialized = False
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the registry.
        
        Args:
            plugin: The plugin to register.
            
        Raises:
            RegistrationError: If the plugin is already registered.
        """
        if plugin.name in self._plugins:
            raise RegistrationError(f"Plugin '{plugin.name}' is already registered")
        
        # Store the plugin
        self._plugins[plugin.name] = plugin
        
        # Register extensions
        plugin.register_extensions(self)
        
        print(f"Registered plugin: {plugin.name} ({plugin.version})")
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """Unregister a plugin and all its extensions.
        
        Args:
            plugin_name: The name of the plugin to unregister.
            
        Raises:
            PluginError: If the plugin is not found.
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' is not registered")
        
        # Remove the plugin
        plugin = self._plugins.pop(plugin_name)
        
        # Remove all extensions registered by this plugin
        for ext_type, extensions in self._extensions.items():
            self._extensions[ext_type] = [
                ext for ext in extensions 
                if not hasattr(ext, '_plugin') or ext._plugin != plugin_name
            ]
        
        print(f"Unregistered plugin: {plugin_name}")
    
    def register_extension(
        self, 
        extension_point: Type[T], 
        extension: T,
        name: Optional[str] = None
    ) -> None:
        """Register an extension for an extension point.
        
        Args:
            extension_point: The extension point to register for.
            extension: The extension instance.
            name: Optional name for the extension. If not provided, the class name is used.
            
        Raises:
            ExtensionError: If the extension is not compatible with the extension point.
        """
        if not isinstance(extension, extension_point.get_interface()):
            raise ExtensionError(
                f"Extension {extension} does not implement the required interface "
                f"for {extension_point.__name__}"
            )
        
        ext_name = name or extension.__class__.__name__
        self._extensions[extension_point].append(extension)
        self._extension_map[extension_point][ext_name] = extension
    
    def get_extensions(self, extension_point: Type[T]) -> List[T]:
        """Get all extensions for an extension point.
        
        Args:
            extension_point: The extension point to get extensions for.
            
        Returns:
            A list of extensions for the given extension point.
        """
        return self._extensions.get(extension_point, [])
    
    def get_extension(self, extension_point: Type[T], name: str) -> Optional[T]:
        """Get a named extension for an extension point.
        
        Args:
            extension_point: The extension point to get the extension for.
            name: The name of the extension.
            
        Returns:
            The extension instance, or None if not found.
        """
        return self._extension_map.get(extension_point, {}).get(name)
    
    def get_plugins(self) -> List[Plugin]:
        """Get all registered plugins."""
        return list(self._plugins.values())
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            name: The name of the plugin.
            
        Returns:
            The plugin instance, or None if not found.
        """
        return self._plugins.get(name)
    
    def get_tools(self) -> List[Tool]:
        """Get all registered tools from all plugins."""
        tools = []
        for plugin in self._plugins.values():
            tools.extend(plugin.get_tools())
        return tools
    
    def get_agents(self) -> List[Type[Agent]]:
        """Get all registered agent classes from all plugins."""
        agents = []
        for plugin in self._plugins.values():
            agents.extend(plugin.get_agents())
        return agents
    
    def get_workflows(self) -> List[Type[Workflow]]:
        """Get all registered workflow classes from all plugins."""
        workflows = []
        for plugin in self._plugins.values():
            workflows.extend(plugin.get_workflows())
        return workflows

# Create a default extension registry
registry = ExtensionRegistry()
