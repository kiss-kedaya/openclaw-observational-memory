"""
Tests for Tool Suggestion Engine
"""

import pytest
from observational_memory.tool_suggestion import ToolSuggestionEngine, ToolSuggestion


def test_social_media_detection():
    engine = ToolSuggestionEngine()
    
    obs = "请帮我分析这个推文 https://twitter.com/user/status/123"
    suggestions = engine.analyze_observation(obs)
    
    assert len(suggestions) > 0
    assert any(s.tool == "agent-reach" for s in suggestions)


def test_browser_detection():
    engine = ToolSuggestionEngine()
    
    obs = "需要打开浏览器填写表单"
    suggestions = engine.analyze_observation(obs)
    
    assert len(suggestions) > 0
    assert any(s.tool == "agent-browser" for s in suggestions)


def test_search_detection():
    engine = ToolSuggestionEngine()
    
    obs = "请搜索一下什么是 OpenClaw"
    suggestions = engine.analyze_observation(obs)
    
    assert len(suggestions) > 0
    assert any(s.tool == "web_search" for s in suggestions)


def test_code_issue_detection():
    engine = ToolSuggestionEngine()
    
    obs = "代码报错了：ImportError: No module named xxx"
    suggestions = engine.analyze_observation(obs)
    
    assert len(suggestions) > 0
    assert any(s.tool == "debugging-wizard" for s in suggestions)


def test_statistics():
    engine = ToolSuggestionEngine()
    
    observations = [
        "请搜索一下",
        "打开浏览器",
        "代码错误",
        "https://twitter.com/test"
    ]
    
    stats = engine.get_tool_statistics(observations)
    
    assert stats["total_suggestions"] > 0
    assert len(stats["by_tool"]) > 0
    assert stats["avg_confidence"] > 0
