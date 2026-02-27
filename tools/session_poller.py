#!/usr/bin/env python3
"""
Session Poller - Polling 模式备用方案
直接读取 OpenClaw 会话文件并同步到 Observational Memory
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# 修复：监控所有 agent 的 sessions 目录
OPENCLAW_SESSIONS_DIRS = [
    Path("C:/Users/34438/.openclaw/agents/main/sessions"),
    Path("C:/Users/34438/.openclaw/agents/openclaw-expert/sessions"),
    Path("C:/Users/34438/.openclaw/agents/full-stack-architect/sessions"),
]

MEMORY_API = "http://localhost:3000/api"
POLL_INTERVAL = 60  # 60 秒检查一次

def get_session_files():
    """获取所有会话文件"""
    all_files = []
    
    for sessions_dir in OPENCLAW_SESSIONS_DIRS:
        if not sessions_dir.exists():
            print(f"[Session Poller] WARN - Sessions directory not found: {sessions_dir}")
            continue
        
        files = list(sessions_dir.glob("**/*.jsonl"))
        print(f"[Session Poller] Found {len(files)} files in {sessions_dir.name}")
        all_files.extend(files)
    
    return all_files

def extract_text_from_content(content):
    """从 content 中提取文本"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # content 是数组，提取所有 text 字段
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text' and 'text' in item:
                    texts.append(item['text'])
                elif 'text' in item:
                    texts.append(item['text'])
        return '\n'.join(texts)
    elif isinstance(content, dict):
        # content 是对象，尝试提取 text 字段
        if 'text' in content:
            return content['text']
    return ''

def parse_session_file(file_path):
    """解析会话文件"""
    messages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('type') == 'message' and 'message' in entry:
                        msg = entry['message']
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        
                        # 提取文本内容
                        text_content = extract_text_from_content(content)
                        
                        if text_content:  # 只添加非空消息
                            messages.append({
                                'role': role,
                                'content': text_content,
                                'timestamp': entry.get('timestamp', datetime.now().isoformat())
                            })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"[Session Poller] ERROR - Failed to parse {file_path}: {e}")
    
    return messages

def sync_session(session_id, messages):
    """同步会话到 Observational Memory"""
    try:
        response = requests.post(
            f"{MEMORY_API}/sessions",
            json={
                "session_id": session_id,
                "messages": messages
            },
            timeout=5
        )
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"[Session Poller] WARN - Service not running")
        return False
    except Exception as e:
        print(f"[Session Poller] ERROR - Failed to sync: {e}")
        return False

def poll_sessions():
    """轮询会话文件"""
    print(f"[Session Poller] Starting... Polling every {POLL_INTERVAL}s")
    print(f"[Session Poller] Watching {len(OPENCLAW_SESSIONS_DIRS)} directories:")
    for sessions_dir in OPENCLAW_SESSIONS_DIRS:
        print(f"  - {sessions_dir}")
    print()
    
    processed = set()
    
    while True:
        try:
            files = get_session_files()
            
            if not files:
                print(f"[Session Poller] No session files found")
                time.sleep(POLL_INTERVAL)
                continue
            
            print(f"[Session Poller] Total files found: {len(files)}")
            
            synced_count = 0
            for file_path in files:
                # 使用文件路径 + 修改时间作为唯一标识
                file_key = f"{file_path}:{file_path.stat().st_mtime}"
                
                if file_key in processed:
                    continue
                
                session_id = file_path.stem
                messages = parse_session_file(file_path)
                
                if messages:
                    if sync_session(session_id, messages):
                        print(f"[Session Poller] OK - Synced {session_id}: {len(messages)} messages")
                        processed.add(file_key)
                        synced_count += 1
                    else:
                        print(f"[Session Poller] ERROR - Failed to sync {session_id}")
            
            if synced_count > 0:
                print(f"[Session Poller] Synced {synced_count} sessions")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("[Session Poller] Stopped by user")
            break
        except Exception as e:
            print(f"[Session Poller] ERROR: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    poll_sessions()
