# 测试 Session Poller 同步功能
import sys
import time
from pathlib import Path

sys.path.insert(0, '.')
from session_poller import get_session_files, parse_session_file, sync_session

print("=" * 60)
print("Session Poller 同步测试")
print("=" * 60)
print()

# 获取所有文件
files = get_session_files()
print(f"找到 {len(files)} 个会话文件")
print()

# 测试解析和同步前 3 个文件
print("测试同步前 3 个文件...")
print()

success_count = 0
error_count = 0

for i, file_path in enumerate(files[:3], 1):
    print(f"[{i}/3] {file_path.name}")
    
    # 解析文件
    messages = parse_session_file(file_path)
    print(f"  解析: {len(messages)} 条消息")
    
    if messages:
        # 同步到 API
        session_id = file_path.stem
        if sync_session(session_id, messages):
            print(f"  同步: 成功")
            success_count += 1
        else:
            print(f"  同步: 失败")
            error_count += 1
    else:
        print(f"  跳过: 无消息")
    
    print()
    time.sleep(0.5)

print("=" * 60)
print(f"测试完成: {success_count} 成功, {error_count} 失败")
print("=" * 60)
