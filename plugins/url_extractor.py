"""
URL Extractor Plugin

Extracts URLs from messages and creates observations.
"""

from plugin_system import ObservationPlugin
from typing import Dict, Any, Optional
import re


class URLExtractorPlugin(ObservationPlugin):
    """Extract URLs from messages"""
    
    @property
    def name(self) -> str:
        return "url-extractor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def extract(self, message: Dict[str, Any]) -> Optional[str]:
        content = message.get("content", "")
        
        # Find URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        if urls:
            return f"Referenced {len(urls)} URL(s): {', '.join(urls[:3])}"
        
        return None
