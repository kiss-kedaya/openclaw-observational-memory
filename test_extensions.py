"""
Tests for Plugin System and i18n

Run with: pytest test_extensions.py -v
"""

import pytest
from pathlib import Path
import shutil
from plugin_system import PluginManager, ObservationPlugin
from i18n import I18n, create_chinese_locale


class TestPluginSystem:
    """Test plugin system"""
    
    def setup_method(self):
        self.test_dir = Path("./test_plugins_workspace")
        self.plugins_dir = self.test_dir / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test plugin
        test_plugin = '''
from plugin_system import ObservationPlugin
from typing import Dict, Any, Optional

class TestPlugin(ObservationPlugin):
    @property
    def name(self) -> str:
        return "test-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def extract(self, message: Dict[str, Any]) -> Optional[str]:
        if "test" in message.get("content", "").lower():
            return "Test observation"
        return None
'''
        (self.plugins_dir / "test_plugin.py").write_text(test_plugin)
    
    def teardown_method(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_discover_plugins(self):
        manager = PluginManager(self.plugins_dir)
        plugins = manager.discover_plugins()
        assert "test_plugin" in plugins
    
    def test_load_plugin(self):
        manager = PluginManager(self.plugins_dir)
        plugin = manager.load_plugin("test_plugin")
        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"
    
    def test_plugin_extract(self):
        manager = PluginManager(self.plugins_dir)
        plugin = manager.load_plugin("test_plugin")
        
        message = {"content": "This is a test message"}
        result = plugin.extract(message)
        assert result == "Test observation"
    
    def test_list_plugins(self):
        manager = PluginManager(self.plugins_dir)
        manager.load_plugin("test_plugin")
        plugins = manager.list_plugins()
        assert len(plugins) == 1
        assert plugins[0]["name"] == "test-plugin"


class TestI18n:
    """Test internationalization"""
    
    def setup_method(self):
        self.test_dir = Path("./test_i18n_workspace")
        self.locales_dir = self.test_dir / "locales"
        self.locales_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_default_locale(self):
        i18n = I18n(self.locales_dir)
        assert i18n.current_locale == "en"
        assert i18n.t("app.title") == "Observational Memory"
    
    def test_set_locale(self):
        i18n = I18n(self.locales_dir)
        create_chinese_locale(self.locales_dir)
        i18n.set_locale("zh")
        assert i18n.current_locale == "zh"
        assert i18n.t("app.title") == "观察记忆"
    
    def test_translation_with_format(self):
        i18n = I18n(self.locales_dir)
        # Add a translation with placeholder
        i18n.translations["en"]["test.format"] = "Hello {name}"
        result = i18n.t("test.format", name="World")
        assert result == "Hello World"
    
    def test_get_available_locales(self):
        i18n = I18n(self.locales_dir)
        create_chinese_locale(self.locales_dir)
        locales = i18n.get_available_locales()
        assert "en" in locales
        assert "zh" in locales


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
