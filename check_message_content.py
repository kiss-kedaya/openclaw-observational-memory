import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 检查几条消息的实际内容
cursor.execute("SELECT content FROM messages LIMIT 5")
messages = cursor.fetchall()

print("Sample messages:")
print()

for i, (content,) in enumerate(messages, 1):
    print(f"[{i}] Length: {len(content)} chars")
    print(f"Content preview: {content[:200]}...")
    print()

# 统计消息长度分布
cursor.execute("SELECT LENGTH(content) as len FROM messages ORDER BY len DESC LIMIT 10")
lengths = cursor.fetchall()

print("Top 10 longest messages:")
for (length,) in lengths:
    print(f"  {length:,} chars")

conn.close()
