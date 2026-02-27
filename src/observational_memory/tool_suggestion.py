"""
Tool Suggestion Engine

Analyzes observations and suggests relevant tools.
"""

import re
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ToolSuggestion:
    """Tool suggestion with confidence score"""
    tool: str
    reason: str
    confidence: float
    context: str = ""


class ToolSuggestionEngine:
    """
    Analyzes observations and suggests tools
    
    Detects patterns and recommends appropriate tools:
    - Social media links → agent-reach
    - Browser interaction → agent-browser
    - Search needs → web_search
    - Code issues → relevant tools
    """
    
    def __init__(self):
        self.patterns = {
            "social_media": [
                r"twitter\.com",
                r"x\.com",
                r"facebook\.com",
                r"instagram\.com",
                r"linkedin\.com",
                r"weibo\.com",
                r"douyin\.com"
            ],
            "browser_keywords": [
                "浏览器", "browser", "网页", "webpage", "点击", "click",
                "填写", "fill", "登录", "login", "截图", "screenshot"
            ],
            "search_keywords": [
                "搜索", "search", "查找", "find", "查询", "query",
                "了解", "learn", "什么是", "what is"
            ],
            "code_keywords": [
                "错误", "error", "报错", "bug", "调试", "debug",
                "代码", "code", "函数", "function", "类", "class"
            ]
        }
    
    def analyze_observation(self, observation: str) -> List[ToolSuggestion]:
        """Analyze observation and generate tool suggestions"""
        suggestions = []
        
        if self._has_social_media_link(observation):
            suggestions.append(ToolSuggestion(
                tool="agent-reach",
                reason="检测到社交媒体链接",
                confidence=0.9,
                context=self._extract_links(observation)
            ))
        
        if self._needs_browser(observation):
            suggestions.append(ToolSuggestion(
                tool="agent-browser",
                reason="需要浏览器交互",
                confidence=0.8,
                context=self._extract_browser_context(observation)
            ))
        
        if self._needs_search(observation):
            suggestions.append(ToolSuggestion(
                tool="web_search",
                reason="需要搜索信息",
                confidence=0.7,
                context=self._extract_search_query(observation)
            ))
        
        if self._has_code_issue(observation):
            suggestions.append(ToolSuggestion(
                tool="debugging-wizard",
                reason="检测到代码问题",
                confidence=0.75,
                context=self._extract_error_context(observation)
            ))
        
        return suggestions
    
    def _has_social_media_link(self, text: str) -> bool:
        for pattern in self.patterns["social_media"]:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _needs_browser(self, text: str) -> bool:
        for keyword in self.patterns["browser_keywords"]:
            if keyword in text.lower():
                return True
        return False
    
    def _needs_search(self, text: str) -> bool:
        for keyword in self.patterns["search_keywords"]:
            if keyword in text.lower():
                return True
        return False
    
    def _has_code_issue(self, text: str) -> bool:
        for keyword in self.patterns["code_keywords"]:
            if keyword in text.lower():
                return True
        return False
    
    def _extract_links(self, text: str) -> str:
        urls = re.findall(r"https?://[^\s]+", text)
        return ", ".join(urls[:3])
    
    def _extract_browser_context(self, text: str) -> str:
        for keyword in self.patterns["browser_keywords"]:
            if keyword in text.lower():
                sentences = text.split("。")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()[:100]
        return ""
    
    def _extract_search_query(self, text: str) -> str:
        questions = re.findall(r"[^。！？]*[？?][^。！？]*", text)
        if questions:
            return questions[0].strip()[:100]
        return ""
    
    def _extract_error_context(self, text: str) -> str:
        errors = re.findall(r"[Ee]rror[^。！？]*", text)
        if errors:
            return errors[0].strip()[:100]
        return ""
    
    def get_tool_statistics(self, observations: List[str]) -> Dict:
        stats = {
            "total_suggestions": 0,
            "by_tool": {},
            "avg_confidence": 0.0
        }
        
        all_confidences = []
        
        for obs in observations:
            suggestions = self.analyze_observation(obs)
            stats["total_suggestions"] += len(suggestions)
            
            for suggestion in suggestions:
                if suggestion.tool not in stats["by_tool"]:
                    stats["by_tool"][suggestion.tool] = 0
                stats["by_tool"][suggestion.tool] += 1
                all_confidences.append(suggestion.confidence)
        
        if all_confidences:
            stats["avg_confidence"] = sum(all_confidences) / len(all_confidences)
        
        return stats
