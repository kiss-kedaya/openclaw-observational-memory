import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 检查空消息
cursor.execute("SELECT COUNT(*) FROM messages WHERE content = '' OR content IS NULL")
empty_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM messages")
total_count = cursor.fetchone()[0]

print(f"Total messages: {total_count:,}")
print(f"Empty messages: {empty_count:,} ({empty_count*100//total_count}%)")
print(f"Non-empty messages: {total_count - empty_count:,}")
print()

# 检查非空消息的统计
cursor.execute("""
    SELECT 
        COUNT(*) as count,
        AVG(LENGTH(content)) as avg_len,
        SUM(LENGTH(content)) as total_len
    FROM messages
    WHERE content != '' AND content IS NOT NULL
""")

stats = cursor.fetchone()
if stats[0] > 0:
    count, avg_len, total_len = stats
    print(f"Non-empty messages:")
    print(f"  Count: {count:,}")
    print(f"  Average length: {avg_len:.1f} chars")
    print(f"  Total length: {total_len:,} chars")
    print(f"  Estimated tokens: {int(total_len // 2.5):,}")

conn.close()
