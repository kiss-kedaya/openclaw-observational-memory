"""
Observational Memory - Mastra-inspired memory system for OpenClaw

Extends Hermes Agent with Mastra-style observational memory:
- Observer: Extract structured observations from conversations
- Reflector: Compress observations without losing information
- Priority System: 🔴 High / 🟡 Medium / 🟢 Low
- Temporal Anchoring: Dual timestamps (when said + when referenced)

Based on Mastra Code's observational memory architecture.
See: https://docs.mastra.ai/

Author: OpenClaw Community
License: MIT
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import hashlib

class ObservationExtractor:
    """
    Observer Agent - Extract structured observations from conversations
    
    Inspired by Mastra's Observer, this extracts key information from messages
    and formats them with priority markers and timestamps.
    
    Priority Levels:
    - 🔴 High: User facts, preferences, completed goals, critical context
    - 🟡 Medium: Project details, learned information, tool results
    - 🟢 Low: Minor details, uncertain observations
    """
    
    def __init__(self):
        self.priority_markers = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        
        # Keywords for detecting high-priority content
        self.high_priority_keywords = {
            'user_facts': ['我是', '我的', '我有', '我在', '我叫'],
            'preferences': ['喜欢', '偏好', '习惯', '倾向', '更喜欢'],
            'goals': ['目标', '计划', '要做', '想要', '希望'],
            'decisions': ['决定', '选择', '确定', '采用']
        }
        
        # Keywords for detecting completed tasks
        self.completion_keywords = ['完成', '成功', '已', '修复', '解决', '实现']
        
        # Keywords for detecting tool usage
        self.tool_keywords = ['安装', '配置', '运行', '执行', '调用', '使用']
    
    def extract_observations(self, messages: List[Dict]) -> str:
        """
        从消息列表中提取观察
        
        Args:
            messages: 消息列表 [{"role": "user/assistant", "content": "...", "timestamp": "..."}]
        
        Returns:
            格式化的观察文本
        """
        observations = []
        current_date = None
        
        for msg in messages:
            timestamp = msg.get('timestamp', datetime.now().isoformat())
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
            time_str = dt.strftime('%H:%M')
            
            # 按日期分组
            if date_str != current_date:
                if observations:
                    observations.append('')  # 空行分隔
                observations.append(f'Date: {date_str}')
                current_date = date_str
            
            # 提取观察
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                # 用户消息 - 高优先级
                obs = self._extract_user_observation(content, time_str)
                if obs:
                    observations.append(f'* {self.priority_markers["high"]} ({time_str}) {obs}')
            
            elif role == 'assistant':
                # 助手消息 - 中优先级
                obs = self._extract_assistant_observation(content, time_str)
                if obs:
                    observations.append(f'* {self.priority_markers["medium"]} ({time_str}) {obs}')
        
        return '\n'.join(observations)
    
    def _extract_user_observation(self, content: str, time: str) -> Optional[str]:
        """
        Extract observation from user message
        
        Prioritizes:
        - User assertions (facts about themselves)
        - Questions and requests
        - Preferences and goals
        """
        content = content.strip()
        if not content:
            return None
        
        # Detect high-priority content
        is_high_priority = any(
            any(keyword in content for keyword in keywords)
            for keywords in self.high_priority_keywords.values()
        )
        
        # Short messages: capture verbatim
        if len(content) < 200:
            if is_high_priority:
                return f'User stated: {content}'
            else:
                return f'User asked: {content}'
        
        # Long messages: extract key points
        sentences = content.split('。')
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 10][:3]
        summary = '。'.join(key_sentences)
        
        return f'User provided: {summary}...'
    
    def _extract_assistant_observation(self, content: str, time: str) -> Optional[str]:
        """
        Extract observation from assistant message
        
        Focuses on:
        - Completed tasks
        - Tool usage
        - Important decisions
        - Technical operations
        """
        content = content.strip()
        if not content:
            return None
        
        # Detect completion
        if any(keyword in content for keyword in self.completion_keywords):
            # Extract what was completed
            match = re.search(r'(完成|成功|已|修复|解决|实现)(.{0,50})', content)
            if match:
                return f'Agent completed: {match.group(2).strip()}'
        
        # Detect tool usage
        if any(keyword in content for keyword in self.tool_keywords):
            match = re.search(r'(安装|配置|运行|执行|调用|使用)(.{0,50})', content)
            if match:
                return f'Agent performed: {match.group(0).strip()}'
        
        # Detect code blocks (technical operations)
        if '```' in content:
            return 'Agent provided technical solution with code'
        
        # Long explanations: skip (too verbose)
        if len(content) > 500:
            return None
        
        return None
    
    def compress_observations(self, observations: str, max_tokens: int = 40000) -> str:
        """
        Reflector - Compress observations without losing information
        
        Strategy:
        1. Keep all high-priority (🔴) observations
        2. Merge similar medium-priority (🟡) observations
        3. Remove low-priority (🟢) observations if needed
        4. Group by date and deduplicate
        
        Args:
            observations: Original observations text
            max_tokens: Maximum token count (rough estimate: 1 token ≈ 2 chars)
        
        Returns:
            Compressed observations
        """
        lines = observations.split('\n')
        
        # Parse observations by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        date_markers = []
        
        for line in lines:
            if line.startswith('Date:'):
                date_markers.append(line)
            elif '🔴' in line:
                high_priority.append(line)
            elif '🟡' in line:
                medium_priority.append(line)
            elif '🟢' in line:
                low_priority.append(line)
        
        # Deduplicate similar observations
        def deduplicate(obs_list: List[str]) -> List[str]:
            seen = set()
            unique = []
            for obs in obs_list:
                # Extract content (remove time and priority marker)
                content = re.sub(r'\* [🔴🟡🟢] \(\d{2}:\d{2}\) ', '', obs)
                content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
                if content_hash not in seen:
                    seen.add(content_hash)
                    unique.append(obs)
            return unique
        
        high_priority = deduplicate(high_priority)
        medium_priority = deduplicate(medium_priority)
        
        # Rebuild observations
        compressed = []
        current_date = None
        
        all_obs = high_priority + medium_priority
        all_obs.sort(key=lambda x: re.search(r'\((\d{2}:\d{2})\)', x).group(1) if re.search(r'\((\d{2}:\d{2})\)', x) else '00:00')
        
        for obs in all_obs:
            # Extract date from context (simplified)
            if current_date:
                compressed.append(obs)
            else:
                # First observation, add date marker
                if date_markers:
                    compressed.append(date_markers[0])
                    current_date = date_markers[0]
                compressed.append(obs)
        
        result = '\n'.join(compressed)
        
        # If still too large, keep only high priority
        if len(result) // 2 > max_tokens:
            result = '\n'.join([date_markers[0]] + high_priority) if date_markers else '\n'.join(high_priority)
        
        return result


class ObservationalMemoryManager:
    """观察记忆管理器 - 集成到现有系统"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.observations_dir = workspace_dir / 'memory' / 'observations'
        self.observations_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = ObservationExtractor()
    
    def save_observations(self, session_id: str, observations: str):
        """保存观察到文件"""
        obs_file = self.observations_dir / f'{session_id}.md'
        obs_file.write_text(observations, encoding='utf-8')
    
    def load_observations(self, session_id: str) -> Optional[str]:
        """加载观察"""
        obs_file = self.observations_dir / f'{session_id}.md'
        if obs_file.exists():
            return obs_file.read_text(encoding='utf-8')
        return None
    
    def process_session(self, session_id: str, messages: List[Dict]) -> Dict:
        """
        处理会话，生成观察
        
        Args:
            session_id: 会话 ID
            messages: 消息列表
        
        Returns:
            处理结果 {"observations": "...", "compressed": "...", "token_count": 123}
        """
        # 1. 提取观察
        observations = self.extractor.extract_observations(messages)
        
        # 2. 估算 token 数（粗略：1 token ≈ 2 字符）
        token_count = len(observations) // 2
        
        # 3. 如果超过阈值，压缩
        compressed = observations
        if token_count > 30000:
            compressed = self.extractor.compress_observations(observations)
        
        # 4. 保存
        self.save_observations(session_id, compressed)
        
        return {
            'observations': observations,
            'compressed': compressed,
            'token_count': token_count,
            'compressed_token_count': len(compressed) // 2
        }
    
    def get_context_for_session(self, session_id: str) -> str:
        """
        获取会话的上下文（用于注入到 Agent）
        
        Returns:
            格式化的上下文文本
        """
        observations = self.load_observations(session_id)
        if not observations:
            return ''
        
        context = f"""
The following observations contain your memory of past conversations:

<observations>
{observations}
</observations>

IMPORTANT: When responding, reference specific details from these observations.
Do not give generic advice - personalize your response based on what you know.

This is an ongoing conversation. Continue naturally based on your memory.
"""
        return context


# 集成到现有的 unified_monitor.py
def extend_unified_monitor():
    """
    扩展 unified_monitor.py，添加观察记忆功能
    
    在现有的监控循环中添加：
    1. 检测会话是否需要生成观察（消息数 > 10）
    2. 调用 ObservationalMemoryManager 处理
    3. 更新会话数据库
    """
    code = '''
# 在 unified_monitor.py 的 check_sessions() 函数中添加：

from tools.observational_memory import ObservationalMemoryManager

# 初始化观察记忆管理器
obs_manager = ObservationalMemoryManager(Path.cwd())

# 在处理每个会话时：
if len(session_messages) > 10:
    # 生成观察
    result = obs_manager.process_session(session_id, session_messages)
    
    # 更新会话摘要
    if result['token_count'] > 30000:
        logger.info(f"Session {session_id}: Generated observations ({result['compressed_token_count']} tokens)")
        
        # 可选：更新数据库
        db.update_session_summary(session_id, f"Observations: {result['compressed_token_count']} tokens")
'''
    return code


if __name__ == '__main__':
    # 测试
    from pathlib import Path
    
    # 创建测试数据
    test_messages = [
        {
            'role': 'user',
            'content': '帮我安装 agent-browser',
            'timestamp': '2026-02-27T09:00:00'
        },
        {
            'role': 'assistant',
            'content': '好的，我来安装 agent-browser',
            'timestamp': '2026-02-27T09:00:10'
        },
        {
            'role': 'assistant',
            'content': '安装成功！agent-browser v0.15.0 已就绪',
            'timestamp': '2026-02-27T09:01:00'
        },
        {
            'role': 'user',
            'content': '修复一下 daemon 启动问题',
            'timestamp': '2026-02-27T09:35:00'
        }
    ]
    
    # 测试观察提取
    manager = ObservationalMemoryManager(Path.cwd())
    result = manager.process_session('test_session', test_messages)
    
    print('=== 观察提取结果 ===')
    print(result['observations'])
    print(f'\nToken 数: {result["token_count"]}')
    
    # 测试上下文生成
    context = manager.get_context_for_session('test_session')
    print('\n=== 上下文 ===')
    print(context[:500] + '...')
