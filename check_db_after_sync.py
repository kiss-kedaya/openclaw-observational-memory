import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

print("=" * 60)
print("Database Status After Full Sync")
print("=" * 60)
print()

# 统计
cursor.execute("SELECT COUNT(*) FROM sessions")
total_sessions = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sessions WHERE message_count > 0")
sessions_with_messages = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM messages")
total_messages = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM observations")
total_observations = cursor.fetchone()[0]

cursor.execute("SELECT SUM(message_count) FROM sessions")
total_msg_count = cursor.fetchone()[0] or 0

cursor.execute("SELECT SUM(token_count) FROM sessions")
total_token_count = cursor.fetchone()[0] or 0

print(f"Total sessions: {total_sessions}")
print(f"Sessions with messages: {sessions_with_messages}")
print(f"Total messages (from messages table): {total_messages}")
print(f"Total message_count (from sessions): {total_msg_count}")
print(f"Total token_count: {total_token_count}")
print(f"Total observations: {total_observations}")
print()

# 显示最大的会话
print("Top 10 sessions by message count:")
cursor.execute("""
    SELECT id, message_count, token_count 
    FROM sessions 
    ORDER BY message_count DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    session_id, msg_count, token_count = row
    print(f"  {session_id[:50]}: {msg_count} messages, {token_count} tokens")

conn.close()

print()
print("=" * 60)
