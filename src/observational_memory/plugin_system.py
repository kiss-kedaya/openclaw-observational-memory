"""
Plugin System for Observational Memory

Allows custom observation extractors and processors.

Features:
- Plugin discovery and loading
- Custom extractors
- Hook system
- Plugin configuration
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from abc import ABC, abstractmethod
import sys

sys.path.insert(0, str(Path(__file__).parent))


class ObservationPlugin(ABC):
    """
    Base class for observation plugins
    
    Plugins can extend observation extraction with custom logic.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @abstractmethod
    def extract(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Extract observation from message
        
        Args:
            message: Message dict with role, content, timestamp
        
        Returns:
            Extracted observation or None
        """
        pass
    
    def initialize(self, config: Dict[str, Any]):
        """Initialize plugin with configuration"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        pass


class PluginManager:
    """
    Plugin manager for loading and managing plugins
    """
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, ObservationPlugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        if not self.plugins_dir.exists():
            return []
        
        plugin_files = []
        for file in self.plugins_dir.glob("*.py"):
            if file.stem != "__init__":
                plugin_files.append(file.stem)
        
        return plugin_files
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None):
        """Load a plugin by name"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
        
        # Import plugin module
        spec = importlib.util.spec_from_file_location(
            plugin_name,
            self.plugins_dir / f"{plugin_name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin class
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ObservationPlugin) and obj != ObservationPlugin:
                plugin = obj()
                if config:
                    plugin.initialize(config)
                self.plugins[plugin_name] = plugin
                return plugin
        
        raise ValueError(f"No plugin class found in {plugin_name}")
    
    def load_all_plugins(self, config: Optional[Dict[str, Dict[str, Any]]] = None):
        """Load all discovered plugins"""
        plugin_names = self.discover_plugins()
        for name in plugin_names:
            try:
                plugin_config = config.get(name) if config else None
                self.load_plugin(name, plugin_config)
            except Exception as e:
                print(f"Failed to load plugin {name}: {e}")
    
    def unload_plugin(self, plugin_name: str):
        """Unload a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].cleanup()
            del self.plugins[plugin_name]
    
    def get_plugin(self, plugin_name: str) -> Optional[ObservationPlugin]:
        """Get a loaded plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins"""
        return [
            {"name": plugin.name, "version": plugin.version}
            for plugin in self.plugins.values()
        ]
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a hook"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                callback(*args, **kwargs)


# Example plugin
class CodeBlockExtractor(ObservationPlugin):
    """
    Example plugin: Extract code blocks from messages
    """
    
    @property
    def name(self) -> str:
        return "code-block-extractor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def extract(self, message: Dict[str, Any]) -> Optional[str]:
        content = message.get("content", "")
        
        if "```" in content:
            return "Agent provided code solution"
        
        return None


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Plugin Manager for Observational Memory")
    parser.add_argument("action", choices=["list", "load", "info"])
    parser.add_argument("--plugin", help="Plugin name")
    
    args = parser.parse_args()
    
    manager = PluginManager(Path.cwd() / "plugins")
    
    if args.action == "list":
        plugins = manager.discover_plugins()
        print(f"Available plugins: {len(plugins)}")
        for plugin in plugins:
            print(f"  - {plugin}")
    
    elif args.action == "load":
        if not args.plugin:
            print("Error: --plugin required")
            exit(1)
        manager.load_plugin(args.plugin)
        print(f"Loaded plugin: {args.plugin}")
    
    elif args.action == "info":
        manager.load_all_plugins()
        plugins = manager.list_plugins()
        print(f"Loaded plugins: {len(plugins)}")
        for plugin in plugins:
            print(f"  - {plugin['name']} v{plugin['version']}")
