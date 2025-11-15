"""
Test script for the AgentSpring plugin system.
"""
import asyncio
import sys
import pytest
from pathlib import Path
from agentspring.plugin import PluginManager

def print_plugin_info(plugin):
    """Print information about a plugin."""
    print(f"\nPlugin: {plugin.name}")
    print(f"Version: {plugin.version}")
    print(f"Description: {plugin.description}")
    print(f"Author: {plugin.author}")
    print(f"State: {plugin.state}")
    print(f"Dependencies: {plugin.dependencies}")

@pytest.mark.asyncio
async def test_plugin_system():
    """Test the plugin system."""
    # Create plugin manager
    plugin_dirs = [str(Path(__file__).parent.parent / "agentspring/plugins")]
    manager = PluginManager(plugin_dirs=plugin_dirs)
    
    print("Discovering plugins...")
    plugins = await manager.discover_plugins()
    print(f"Found {len(plugins)} plugins: {plugins}")
    
    # Load and test each plugin
    for plugin_name in plugins:
        try:
            print(f"\n--- Testing plugin: {plugin_name} ---")
            
            # Load the plugin
            print("Loading plugin...")
            plugin = await manager.load_plugin(plugin_name)
            print_plugin_info(plugin)
            
            # Test plugin functionality if available
            if hasattr(plugin, 'greet'):
                print("\nTesting greet method:")
                greeting = await plugin.greet("Test User")
                print(f"Greeting: {greeting}")
            
            # Unload the plugin
            print("\nUnloading plugin...")
            await manager.unload_plugin(plugin_name)
            print(f"Plugin {plugin_name} unloaded successfully")
            
        except Exception as e:
            print(f"Error testing plugin {plugin_name}: {str(e)}", file=sys.stderr)
            raise