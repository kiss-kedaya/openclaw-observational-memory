# 检查刚刚同步的会话
import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

print("Checking synced sessions:")
print()

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
        print(f"OK - {session_id[:40]}...")
        print(f"     Messages: {msg_count}, Tokens: {token_count}")
    else:
        print(f"NOT FOUND - {session_id[:40]}...")
    print()

conn.close()
