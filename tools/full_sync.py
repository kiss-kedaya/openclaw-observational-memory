# 完整同步所有会话文件
import sys
import time
from pathlib import Path

sys.path.insert(0, '.')
from session_poller import get_session_files, parse_session_file, sync_session

print("=" * 70)
print("Session Poller - 完整同步")
print("=" * 70)
print()

# 获取所有文件
files = get_session_files()
print(f"找到 {len(files)} 个会话文件")
print()

# 统计
success_count = 0
error_count = 0
skip_count = 0
total_messages = 0

print("开始同步...")
print()

for i, file_path in enumerate(files, 1):
    # 显示进度
    if i % 10 == 0:
        print(f"进度: {i}/{len(files)} ({i*100//len(files)}%)")
    
    # 解析文件
    messages = parse_session_file(file_path)
    
    if not messages:
        skip_count += 1
        continue
    
    # 同步到 API
    session_id = file_path.stem
    try:
        if sync_session(session_id, messages):
            success_count += 1
            total_messages += len(messages)
        else:
            error_count += 1
            print(f"  ERROR: {file_path.name} - 同步失败")
    except Exception as e:
        error_count += 1
        print(f"  ERROR: {file_path.name} - {e}")
    
    # 避免过快请求
    if i % 10 == 0:
        time.sleep(0.5)

print()
print("=" * 70)
print("同步完成")
print("=" * 70)
print(f"总文件数: {len(files)}")
print(f"成功同步: {success_count}")
print(f"失败: {error_count}")
print(f"跳过（无消息）: {skip_count}")
print(f"总消息数: {total_messages}")
print("=" * 70)
