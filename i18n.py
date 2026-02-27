"""
Internationalization (i18n) Support

Provides multi-language support for observational memory.

Features:
- Language detection
- Translation loading
- Locale management
"""

import json
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """
    Internationalization manager
    """
    
    def __init__(self, locales_dir: Path, default_locale: str = "zh"):
        self.locales_dir = locales_dir
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, str]] = {}
        
        # Load default locale
        self.load_locale(default_locale)
    
    def load_locale(self, locale: str):
        """Load translations for a locale"""
        locale_file = self.locales_dir / f"{locale}.json"
        
        if not locale_file.exists():
            if locale != self.default_locale:
                print(f"Locale {locale} not found, using default")
                return
            else:
                # Create default locale file
                self._create_default_locale()
                locale_file = self.locales_dir / f"{locale}.json"
        
        with open(locale_file, "r", encoding="utf-8") as f:
            self.translations[locale] = json.load(f)
    
    def _create_default_locale(self):
        """Create default English locale"""
        self.locales_dir.mkdir(parents=True, exist_ok=True)
        
        default_translations = {
            "app.title": "Observational Memory",
            "app.description": "Mastra-inspired memory system",
            "dashboard.title": "Dashboard",
            "dashboard.total_sessions": "Total Sessions",
            "dashboard.total_observations": "Total Observations",
            "dashboard.total_tokens": "Total Tokens",
            "dashboard.vector_embeddings": "Vector Embeddings",
            "sessions.title": "Sessions",
            "sessions.search": "Search sessions",
            "sessions.delete": "Delete",
            "search.title": "Semantic Search",
            "search.query": "Enter search query",
            "search.results": "Number of results",
            "search.similarity": "Minimum similarity",
            "search.button": "Search",
            "analytics.title": "Analytics",
            "analytics.priority_distribution": "Priority Distribution",
            "analytics.timeline": "Session Timeline",
            "analytics.token_usage": "Token Usage by Session",
            "priority.high": "High",
            "priority.medium": "Medium",
            "priority.low": "Low"
        }
        
        locale_file = self.locales_dir / f"{self.default_locale}.json"
        with open(locale_file, "w", encoding="utf-8") as f:
            json.dump(default_translations, f, indent=2, ensure_ascii=False)
        
        self.translations[self.default_locale] = default_translations
    
    def set_locale(self, locale: str):
        """Set current locale"""
        if locale not in self.translations:
            self.load_locale(locale)
        self.current_locale = locale
    
    def t(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key
        
        Args:
            key: Translation key
            locale: Optional locale override
            **kwargs: Format arguments
        
        Returns:
            Translated string
        """
        locale = locale or self.current_locale
        
        if locale not in self.translations:
            locale = self.default_locale
        
        translation = self.translations[locale].get(key, key)
        
        if kwargs:
            translation = translation.format(**kwargs)
        
        return translation
    
    def get_available_locales(self) -> list:
        """Get list of available locales"""
        if not self.locales_dir.exists():
            return [self.default_locale]
        
        return [f.stem for f in self.locales_dir.glob("*.json")]


# Create Chinese locale
def create_chinese_locale(locales_dir: Path):
    """Create Chinese (Simplified) locale"""
    translations = {
        "app.title": "观察记忆",
        "app.description": "Mastra 启发的记忆系统",
        "dashboard.title": "仪表板",
        "dashboard.total_sessions": "总会话数",
        "dashboard.total_observations": "总观察数",
        "dashboard.total_tokens": "总 Token 数",
        "dashboard.vector_embeddings": "向量嵌入数",
        "sessions.title": "会话",
        "sessions.search": "搜索会话",
        "sessions.delete": "删除",
        "search.title": "语义搜索",
        "search.query": "输入搜索查询",
        "search.results": "结果数量",
        "search.similarity": "最小相似度",
        "search.button": "搜索",
        "analytics.title": "分析",
        "analytics.priority_distribution": "优先级分布",
        "analytics.timeline": "会话时间线",
        "analytics.token_usage": "会话 Token 使用量",
        "priority.high": "高",
        "priority.medium": "中",
        "priority.low": "低"
    }
    
    locales_dir.mkdir(parents=True, exist_ok=True)
    locale_file = locales_dir / "zh.json"
    
    with open(locale_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="i18n Manager for Observational Memory")
    parser.add_argument("action", choices=["init", "list", "translate"])
    parser.add_argument("--locale", help="Locale code")
    parser.add_argument("--key", help="Translation key")
    
    args = parser.parse_args()
    
    locales_dir = Path.cwd() / "locales"
    i18n = I18n(locales_dir)
    
    if args.action == "init":
        if args.locale == "zh":
            create_chinese_locale(locales_dir)
            print("Created Chinese locale")
        else:
            print("Only 'zh' locale supported for init")
    
    elif args.action == "list":
        locales = i18n.get_available_locales()
        print(f"Available locales: {', '.join(locales)}")
    
    elif args.action == "translate":
        if not args.key:
            print("Error: --key required")
            exit(1)
        
        if args.locale:
            i18n.set_locale(args.locale)
        
        translation = i18n.t(args.key)
        print(f"{args.key} = {translation}")
