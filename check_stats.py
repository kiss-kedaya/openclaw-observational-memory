import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 统计消息长度分布
cursor.execute("""
    SELECT 
        COUNT(*) as count,
        AVG(LENGTH(content)) as avg_len,
        MIN(LENGTH(content)) as min_len,
        MAX(LENGTH(content)) as max_len,
        SUM(LENGTH(content)) as total_len
    FROM messages
""")

stats = cursor.fetchone()
count, avg_len, min_len, max_len, total_len = stats

print("Message Statistics:")
print(f"  Total messages: {count:,}")
print(f"  Average length: {avg_len:.1f} chars")
print(f"  Min length: {min_len} chars")
print(f"  Max length: {max_len:,} chars")
print(f"  Total length: {total_len:,} chars")
print()

# 估算 token 数（使用更准确的方法）
# 假设平均每 3 个字符 = 1 token（考虑中英文混合）
estimated_tokens = total_len // 3

print(f"Estimated tokens (chars/3): {estimated_tokens:,}")
print(f"Current token count in DB: 41,902")
print(f"Difference: {estimated_tokens - 41902:,}")

conn.close()
