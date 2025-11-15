from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
from pathlib import Path
import importlib
import inspect
import logging

logger = logging.getLogger(__name__)

class PluginState(Enum):
    """Represents the state of a plugin."""
    UNLOADED = auto()
    LOADED = auto()
    ENABLED = auto()
    DISABLED = auto()
    ERROR = auto()

@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str = ""
    author: str = ""
    license: str = "MIT"
    requires: List[str] = field(default_factory=list)  # List of required plugin names
    conflicts: List[str] = field(default_factory=list)  # List of conflicting plugin names
    python_requires: str = ">=3.9"  # Python version requirement
    dependencies: Dict[str, str] = field(default_factory=dict)  # Package dependencies
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """Create PluginMetadata from a dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        })

class BasePlugin:
    """Base class for all plugins."""
    
    def __init__(self):
        self._state = PluginState.UNLOADED
        self._metadata: Optional[PluginMetadata] = None
        self._module = None
        self._path: Optional[Path] = None
        self._resources = {}
        
    @property
    def state(self) -> PluginState:
        """Get the current state of the plugin."""
        return self._state
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        if self._metadata is None:
            raise ValueError("Plugin metadata not loaded")
        return self._metadata
    
    @property
    def name(self) -> str:
        """Get the plugin name."""
        return self.metadata.name
    
    async def load(self) -> None:
        """Load the plugin."""
        if self._state != PluginState.UNLOADED:
            raise RuntimeError(f"Plugin {self.name} is already loaded")
        
        self._state = PluginState.LOADED
        logger.info(f"Loaded plugin: {self.name}")
    
    async def unload(self) -> None:
        """Unload the plugin and clean up resources."""
        if self._state == PluginState.UNLOADED:
            return
            
        if hasattr(self, 'on_disable'):
            await self.on_disable()
            
        # Clean up resources
        for resource in self._resources.values():
            if hasattr(resource, 'close'):
                if inspect.iscoroutinefunction(resource.close):
                    await resource.close()
                else:
                    resource.close()
        
        self._resources.clear()
        self._state = PluginState.UNLOADED
        logger.info(f"Unloaded plugin: {self.name}")
    
    async def enable(self) -> None:
        """Enable the plugin."""
        if self._state != PluginState.LOADED:
            raise RuntimeError(f"Cannot enable plugin {self.name} in state {self._state}")
        
        if hasattr(self, 'on_enable'):
            await self.on_enable()
            
        self._state = PluginState.ENABLED
        logger.info(f"Enabled plugin: {self.name}")
    
    async def disable(self) -> None:
        """Disable the plugin."""
        if self._state != PluginState.ENABLED:
            return
            
        if hasattr(self, 'on_disable'):
            await self.on_disable()
            
        self._state = PluginState.DISABLED
        logger.info(f"Disabled plugin: {self.name}")
    
    def register_resource(self, name: str, resource: Any) -> None:
        """Register a resource that needs cleanup."""
        self._resources[name] = resource
    
    def get_resource(self, name: str) -> Any:
        """Get a registered resource."""
        return self._resources.get(name)

    # Lifecycle hooks (to be overridden by plugins)
    async def on_load(self) -> None:
        """Called when the plugin is loaded."""
        pass
        
    async def on_enable(self) -> None:
        """Called when the plugin is enabled."""
        pass
        
    async def on_disable(self) -> None:
        """Called when the plugin is disabled."""
        pass
        
    async def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        pass
