import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 检查数据库编码
cursor.execute("PRAGMA encoding")
encoding = cursor.fetchone()
print(f"Database encoding: {encoding[0]}")

# 读取最新的观察记录
cursor.execute("SELECT content FROM observations WHERE session_id = 'test-chinese-20260227195756' LIMIT 1")
row = cursor.fetchone()

if row:
    content = row[0]
    print(f"\nContent from DB: {content}")
    print(f"Content bytes: {content.encode('utf-8')}")
    print(f"Content repr: {repr(content)}")

conn.close()
