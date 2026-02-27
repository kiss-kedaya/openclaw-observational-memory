# observational_memory.py - OpenClaw Hook for Observational Memory

import requests
import json
from datetime import datetime
import os

MEMORY_API = "http://localhost:3000/api"

def on_message(event):
    """每条消息都记录到 Observational Memory"""
    try:
        session_id = event.get('session_id', 'default')
        message = event.get('message', '')
        role = event.get('role', 'user')
        
        # 创建或更新会话
        response = requests.post(f"{MEMORY_API}/sessions", json={
            "session_id": session_id,
            "messages": [{
                "role": role,
                "content": message,
                "timestamp": datetime.now().isoformat()
            }]
        }, timeout=5)
        
        if response.status_code == 200:
            print(f"[Observational Memory] ✅ 记录消息: {session_id}")
        else:
            print(f"[Observational Memory] ⚠️ 记录失败: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"[Observational Memory] ⚠️ 服务未启动")
    except Exception as e:
        print(f"[Observational Memory] ❌ 错误: {e}")

def on_session_end(event):
    """会话结束时触发分析"""
    try:
        session_id = event.get('session_id')
        
        # 获取观察记录
        response = requests.get(f"{MEMORY_API}/observations/{session_id}", timeout=5)
        
        if response.status_code == 200:
            observations = response.json()
            print(f"[Observational Memory] 📊 会话 {session_id} 共 {len(observations)} 条观察")
        
    except Exception as e:
        print(f"[Observational Memory] ❌ 错误: {e}")

# Hook 元数据
__hook_name__ = "Observational Memory"
__hook_version__ = "1.1.0"
__hook_description__ = "自动记录所有对话到 Observational Memory 系统"
__hook_author__ = "OpenClaw Community"
