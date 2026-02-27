# 检查数据库中的会话数据
import sqlite3
from datetime import datetime

print("=" * 60)
print("数据库验证")
print("=" * 60)
print()

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 1. 检查会话总数
cursor.execute("SELECT COUNT(*) FROM sessions")
total_sessions = cursor.fetchone()[0]
print(f"总会话数: {total_sessions}")

# 2. 检查有消息的会话
cursor.execute("SELECT COUNT(*) FROM sessions WHERE message_count > 0")
sessions_with_messages = cursor.fetchone()[0]
print(f"有消息的会话: {sessions_with_messages}")

# 3. 检查消息总数
cursor.execute("SELECT COUNT(*) FROM messages")
total_messages = cursor.fetchone()[0]
print(f"总消息数: {total_messages}")

# 4. 检查观察总数
cursor.execute("SELECT COUNT(*) FROM observations")
total_observations = cursor.fetchone()[0]
print(f"总观察数: {total_observations}")

print()

# 5. 显示最近的会话
print("最近的 5 个会话:")
cursor.execute("""
    SELECT id, message_count, token_count, updated_at 
    FROM sessions 
    WHERE message_count > 0
    ORDER BY updated_at DESC 
    LIMIT 5
""")

for row in cursor.fetchall():
    session_id, msg_count, token_count, updated_at = row
    print(f"  - {session_id[:40]}...")
    print(f"    消息: {msg_count}, Token: {token_count}")
    print(f"    更新: {updated_at}")
    print()

# 6. 检查新同步的会话
print("刚刚同步的 3 个会话:")
test_sessions = [
    '025d36f8-f070-4af9-8598-14367dc046a6',
    '0421a4af-e3cb-4fc3-b738-3b847e895ef3',
    '044a2f6e-c21b-4462-a4b4-9d9c75808178'
]

for session_id in test_sessions:
    cursor.execute("""
        SELECT message_count, token_count 
        FROM sessions 
        WHERE id = ?
    """, (session_id,))
    
    result = cursor.fetchone()
    if result:
        msg_count, token_count = result
        print(f"  ✓ {session_id[:40]}...")
        print(f"    消息: {msg_count}, Token: {token_count}")
    else:
        print(f"  ✗ {session_id[:40]}... (未找到)")
    print()

conn.close()

print("=" * 60)
print("数据库验证完成")
print("=" * 60)
