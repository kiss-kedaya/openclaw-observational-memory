# 重试失败的文件
import sys
import time

sys.path.insert(0, '.')
from session_poller import parse_session_file, sync_session
from pathlib import Path

# 失败的文件列表
failed_files = [
    "da96a524-48b7-4cf9-b0b1-66d85ec5fe26.jsonl",
    "3c2653f4-e065-4898-949b-bd1ac708bfa5.jsonl",
    "403bdb32-1239-47cd-8c62-c165e968801e.jsonl",
    "4253bf92-4009-4615-b91e-0972c79f5a0b.jsonl",
    "55815750-efec-4afa-ae57-6dbf99efeadd.jsonl",
    "9dbdbd3e-8934-4772-9c40-0de911851064.jsonl",
    "9e1101d9-138b-49a6-ac55-fd013835c029.jsonl",
    "9f7b19c5-4150-4e5b-90fd-db57a8ee4afb.jsonl",
    "a7ae3bde-adcd-47d8-942e-774bbc60a306.jsonl",
]

print("Retrying failed files with longer timeout...")
print()

# 增加超时时间
import requests
original_timeout = 5

success_count = 0
still_failed = []

for filename in failed_files:
    # 查找文件
    file_path = None
    for sessions_dir in [
        Path("C:/Users/34438/.openclaw/agents/main/sessions"),
        Path("C:/Users/34438/.openclaw/agents/openclaw-expert/sessions"),
        Path("C:/Users/34438/.openclaw/agents/full-stack-architect/sessions"),
    ]:
        candidate = sessions_dir / filename
        if candidate.exists():
            file_path = candidate
            break
    
    if not file_path:
        print(f"NOT FOUND: {filename}")
        continue
    
    print(f"Retrying: {filename}")
    
    # 解析
    messages = parse_session_file(file_path)
    print(f"  Messages: {len(messages)}")
    
    if messages:
        # 使用更长的超时时间
        session_id = file_path.stem
        try:
            response = requests.post(
                "http://localhost:3000/api/sessions",
                json={"session_id": session_id, "messages": messages},
                timeout=30  # 增加到 30 秒
            )
            if response.status_code == 200:
                print(f"  SUCCESS")
                success_count += 1
            else:
                print(f"  FAILED: {response.status_code}")
                still_failed.append(filename)
        except Exception as e:
            print(f"  ERROR: {e}")
            still_failed.append(filename)
    
    time.sleep(1)
    print()

print("=" * 60)
print(f"Retry complete: {success_count} success, {len(still_failed)} still failed")
if still_failed:
    print("Still failed:")
    for f in still_failed:
        print(f"  - {f}")
print("=" * 60)
