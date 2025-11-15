# agentspring/plugin/manager.py
import asyncio
import importlib
import importlib.util
import inspect
import json
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Any, Set, Tuple
from typing_extensions import Protocol

from .base import BasePlugin, PluginMetadata, PluginState
from .exceptions import (
    PluginError,
    PluginLoadError,
    PluginDependencyError,
    PluginConflictError,
    PluginVersionError,
)

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages loading, unloading, and accessing plugins."""
    
    def __init__(self, plugin_dirs: List[str] = None):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self._plugin_paths: Dict[str, Path] = {}
        self._plugin_modules: Dict[str, Any] = {}
        self._plugin_dirs = [Path(d) for d in (plugin_dirs or [])]
        self._dependency_graph: Dict[str, Set[str]] = {}
        
    async def discover_plugins(self) -> List[str]:
        """Discover plugins in configured plugin directories."""
        discovered = []
        
        for plugin_dir in self._plugin_dirs:
            if not plugin_dir.exists():
                logger.warning(f"Plugin directory {plugin_dir} does not exist")
                continue
                
            for entry in plugin_dir.iterdir():
                if not entry.is_dir() or entry.name.startswith('_') or entry.name.startswith('.'):
                    continue
                    
                plugin_name = entry.name
                plugin_path = entry / 'plugin.json'
                
                if plugin_path.exists():
                    try:
                        with open(plugin_path, 'r') as f:
                            metadata = PluginMetadata.from_dict(json.load(f))
                            self.plugin_metadata[plugin_name] = metadata
                            self._plugin_paths[plugin_name] = entry
                            discovered.append(plugin_name)
                            logger.info(f"Discovered plugin: {plugin_name} v{metadata.version}")
                    except Exception as e:
                        logger.error(f"Error loading plugin metadata from {plugin_path}: {e}")
                        
        return discovered
    
    async def load_plugin(self, plugin_name: str) -> BasePlugin:
        """Load a plugin by name."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
            
        if plugin_name not in self.plugin_metadata:
            raise PluginLoadError(f"Plugin {plugin_name} not found")
            
        metadata = self.plugin_metadata[plugin_name]
        
        # Check Python version
        if not self._check_python_version(metadata.python_requires):
            raise PluginVersionError(
                f"Plugin {plugin_name} requires Python {metadata.python_requires}"
            )
            
        # Check for conflicts
        await self._check_conflicts(plugin_name)
        
        # Load dependencies first
        await self._load_dependencies(metadata.requires)
        
        try:
            # Add plugin directory to Python path
            plugin_path = self._plugin_paths[plugin_name]
            if str(plugin_path) not in sys.path:
                sys.path.insert(0, str(plugin_path))
                
            # Import the plugin module
            module_name = f"plugins.{plugin_name}.plugin"
            spec = importlib.util.spec_from_file_location(
                module_name,
                plugin_path / "plugin.py"
            )
            
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Could not load plugin {plugin_name}: No module found")
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find and instantiate the plugin class
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                raise PluginLoadError(f"No plugin class found in {plugin_name}")
                
            plugin = plugin_class()
            plugin._metadata = metadata
            plugin._path = plugin_path
            plugin._module = module
            
            # Initialize the plugin
            await plugin.load()
            if hasattr(plugin, 'on_load'):
                await plugin.on_load()
                
            self.plugins[plugin_name] = plugin
            logger.info(f"Successfully loaded plugin: {plugin_name}")
            
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {str(e)}", exc_info=True)
            if plugin_name in self.plugins:
                await self.unload_plugin(plugin_name)
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {str(e)}")
    
    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            return
            
        plugin = self.plugins[plugin_name]
        
        # Disable first if enabled
        if plugin.state == PluginState.ENABLED:
            await plugin.disable()
            
        # Unload the plugin
        await plugin.unload()
        
        # Remove from tracking
        del self.plugins[plugin_name]
        
        # Clean up module
        module_name = f"plugins.{plugin_name}.plugin"
        if module_name in sys.modules:
            del sys.modules[module_name]
            
        logger.info(f"Unloaded plugin: {plugin_name}")
    
    async def enable_plugin(self, plugin_name: str) -> None:
        """Enable a plugin."""
        if plugin_name not in self.plugins:
            raise PluginError(f"Plugin {plugin_name} is not loaded")
            
        plugin = self.plugins[plugin_name]
        if plugin.state == PluginState.ENABLED:
            return
            
        await plugin.enable()
    
    async def disable_plugin(self, plugin_name: str) -> None:
        """Disable a plugin."""
        if plugin_name not in self.plugins:
            return
            
        plugin = self.plugins[plugin_name]
        if plugin.state != PluginState.ENABLED:
            return
            
        await plugin.disable()
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_plugins(self) -> Dict[str, BasePlugin]:
        """Get all loaded plugins."""
        return self.plugins.copy()
    
    async def _load_dependencies(self, dependencies: List[str]) -> None:
        """Load all dependencies for a plugin."""
        for dep_name in dependencies:
            if dep_name not in self.plugins:
                try:
                    await self.load_plugin(dep_name)
                except Exception as e:
                    raise PluginDependencyError(
                        f"Failed to load dependency {dep_name}: {str(e)}"
                    )
    
    def _check_python_version(self, version_spec: str) -> bool:
        """Check if the current Python version satisfies the requirement."""
        from packaging import version
        import platform
        
        current_version = platform.python_version()
        return version.parse(current_version) >= version.parse(version_spec.lstrip('>='))
    
    async def _check_conflicts(self, plugin_name: str) -> None:
        """Check for plugin conflicts."""
        if plugin_name not in self.plugin_metadata:
            return
            
        metadata = self.plugin_metadata[plugin_name]
        
        # Check for conflicting plugins
        for loaded_name in self.plugins:
            loaded_metadata = self.plugin_metadata.get(loaded_name)
            if not loaded_metadata:
                continue
                
            if loaded_name in metadata.conflicts or plugin_name in loaded_metadata.conflicts:
                raise PluginConflictError(
                    f"Plugin {plugin_name} conflicts with {loaded_name}"
                )
    
    @staticmethod
    def _find_plugin_class(module: Any) -> Optional[Type[BasePlugin]]:
        """Find the plugin class in a module."""
        for name, obj in module.__dict__.items():
            if (
                isinstance(obj, type)
                and issubclass(obj, BasePlugin)
                and obj is not BasePlugin
            ):
                return obj
        return None