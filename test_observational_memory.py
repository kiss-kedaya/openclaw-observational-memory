"""
Tests for Observational Memory

Run with: pytest test_observational_memory.py -v
"""

import pytest
from pathlib import Path
from datetime import datetime
from observational_memory import (
    ObservationExtractor,
    ObservationalMemoryManager
)


class TestObservationExtractor:
    """Test the Observer component"""
    
    def setup_method(self):
        self.extractor = ObservationExtractor()
    
    def test_extract_user_observation_short(self):
        """Test extracting short user messages"""
        content = "帮我安装 agent-browser"
        time = "09:00"
        
        result = self.extractor._extract_user_observation(content, time)
        
        assert result is not None
        assert "User" in result  # Can be "User stated" or "User asked"
        assert "agent-browser" in result
    
    def test_extract_user_observation_long(self):
        """Test extracting long user messages"""
        content = "我需要一个工具来自动化浏览器操作。" * 20  # Long message
        time = "09:00"
        
        result = self.extractor._extract_user_observation(content, time)
        
        assert result is not None
        assert "User provided" in result
    
    def test_extract_assistant_completion(self):
        """Test detecting completed tasks"""
        content = "安装成功！agent-browser v0.15.0 已就绪"
        time = "09:01"
        
        result = self.extractor._extract_assistant_observation(content, time)
        
        assert result is not None
        assert "Agent completed" in result
    
    def test_extract_assistant_tool_usage(self):
        """Test detecting tool usage"""
        content = "我来执行 npm install agent-browser"
        time = "09:00"
        
        result = self.extractor._extract_assistant_observation(content, time)
        
        assert result is not None
        assert "Agent performed" in result
    
    def test_extract_observations_full(self):
        """Test full observation extraction"""
        messages = [
            {
                "role": "user",
                "content": "帮我安装 agent-browser",
                "timestamp": "2026-02-27T09:00:00"
            },
            {
                "role": "assistant",
                "content": "好的，我来安装",
                "timestamp": "2026-02-27T09:00:10"
            },
            {
                "role": "assistant",
                "content": "安装成功！",
                "timestamp": "2026-02-27T09:01:00"
            }
        ]
        
        result = self.extractor.extract_observations(messages)
        
        assert "Date: 2026-02-27" in result
        assert "🔴" in result  # High priority marker
        assert "🟡" in result  # Medium priority marker
        assert "09:00" in result
        assert "09:01" in result
    
    def test_compress_observations(self):
        """Test observation compression"""
        observations = """Date: 2026-02-27
* 🔴 (09:00) User stated: 帮我安装 agent-browser
* 🟡 (09:01) Agent completed: 安装成功
* 🟢 (09:02) Agent provided minor detail
* 🔴 (09:03) User stated: 修复 daemon 问题
"""
        
        compressed = self.extractor.compress_observations(observations, max_tokens=100)
        
        # Should keep high priority
        assert "🔴" in compressed
        assert "User stated" in compressed
        
        # May or may not keep medium priority (depends on size)
        # Should remove low priority if needed
        assert compressed.count("🟢") <= observations.count("🟢")


class TestObservationalMemoryManager:
    """Test the Memory Manager"""
    
    def setup_method(self):
        self.test_dir = Path("./test_workspace")
        self.test_dir.mkdir(exist_ok=True)
        self.manager = ObservationalMemoryManager(self.test_dir)
    
    def teardown_method(self):
        """Clean up test files"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_save_and_load_observations(self):
        """Test saving and loading observations"""
        session_id = "test_session_123"
        observations = "Date: 2026-02-27\n* 🔴 (09:00) Test observation"
        
        # Save
        self.manager.save_observations(session_id, observations)
        
        # Load
        loaded = self.manager.load_observations(session_id)
        
        assert loaded == observations
    
    def test_process_session(self):
        """Test full session processing"""
        session_id = "test_session_456"
        messages = [
            {
                "role": "user",
                "content": "帮我安装工具",
                "timestamp": "2026-02-27T09:00:00"
            },
            {
                "role": "assistant",
                "content": "安装成功",
                "timestamp": "2026-02-27T09:01:00"
            }
        ]
        
        result = self.manager.process_session(session_id, messages)
        
        assert "observations" in result
        assert "compressed" in result
        assert "token_count" in result
        assert result["token_count"] > 0
    
    def test_get_context_for_session(self):
        """Test context generation"""
        session_id = "test_session_789"
        observations = "Date: 2026-02-27\n* 🔴 (09:00) Test"
        
        self.manager.save_observations(session_id, observations)
        context = self.manager.get_context_for_session(session_id)
        
        assert "<observations>" in context
        assert "</observations>" in context
        assert "Test" in context
    
    def test_empty_session(self):
        """Test handling empty sessions"""
        context = self.manager.get_context_for_session("nonexistent_session")
        assert context == ""


class TestPriorityDetection:
    """Test priority detection logic"""
    
    def setup_method(self):
        self.extractor = ObservationExtractor()
    
    def test_high_priority_user_facts(self):
        """Test detecting user facts as high priority"""
        content = "我是一名开发者"
        result = self.extractor._extract_user_observation(content, "09:00")
        
        assert result is not None
        assert "User stated" in result
    
    def test_high_priority_preferences(self):
        """Test detecting preferences as high priority"""
        content = "我喜欢用 Python 编程"
        result = self.extractor._extract_user_observation(content, "09:00")
        
        assert result is not None
        assert "User stated" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=observational_memory"])
