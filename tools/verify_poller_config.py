# 验证 Session Poller 配置
import sys
from pathlib import Path

print("=" * 60)
print("Session Poller 配置验证")
print("=" * 60)
print()

# 导入配置
sys.path.insert(0, '.')
from session_poller import OPENCLAW_SESSIONS_DIRS, get_session_files

print(f"配置的目录数量: {len(OPENCLAW_SESSIONS_DIRS)}")
print()

# 检查每个目录
for i, sessions_dir in enumerate(OPENCLAW_SESSIONS_DIRS, 1):
    print(f"[{i}] {sessions_dir}")
    print(f"    存在: {sessions_dir.exists()}")
    
    if sessions_dir.exists():
        files = list(sessions_dir.glob("**/*.jsonl"))
        print(f"    文件数: {len(files)}")
        
        if files:
            total_size = sum(f.stat().st_size for f in files)
            print(f"    总大小: {total_size / 1024 / 1024:.2f} MB")
    print()

# 获取所有文件
print("获取所有会话文件...")
all_files = get_session_files()
print(f"总计: {len(all_files)} 个会话文件")
print()

# 显示示例文件
if all_files:
    print("示例文件（前 5 个）:")
    for f in all_files[:5]:
        print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
print()

print("=" * 60)
print("配置验证完成")
print("=" * 60)
