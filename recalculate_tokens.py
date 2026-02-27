# 重新计算所有会话的 token 数
import sqlite3
import re

def estimate_tokens(text):
    """估算文本的 token 数量"""
    if not text:
        return 1
    
    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    
    # 中文字符：每个字符约 2 tokens
    token_count = chinese_chars * 2
    
    # 统计英文单词
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    # 英文单词：每个词约 1.3 tokens
    token_count += int(english_words * 1.3)
    
    # 其他字符（标点、数字等）
    other_chars = len(text) - chinese_chars - sum(len(w) for w in re.findall(r'\b[a-zA-Z]+\b', text))
    token_count += int(other_chars * 0.5)
    
    return max(token_count, 1)

print("=" * 70)
print("Recalculating Token Counts")
print("=" * 70)
print()

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 获取所有会话
cursor.execute("SELECT id FROM sessions")
sessions = cursor.fetchall()

print(f"Found {len(sessions)} sessions")
print()

total_tokens = 0
updated_count = 0

for (session_id,) in sessions:
    # 获取该会话的所有消息
    cursor.execute(
        "SELECT content FROM messages WHERE session_id = ?",
        (session_id,)
    )
    messages = cursor.fetchall()
    
    if not messages:
        continue
    
    # 计算 token 数
    session_tokens = sum(estimate_tokens(content) for (content,) in messages)
    
    # 更新数据库
    cursor.execute(
        "UPDATE sessions SET token_count = ? WHERE id = ?",
        (session_tokens, session_id)
    )
    
    total_tokens += session_tokens
    updated_count += 1
    
    if updated_count % 20 == 0:
        print(f"Progress: {updated_count}/{len(sessions)} sessions")

conn.commit()
conn.close()

print()
print("=" * 70)
print("Recalculation Complete")
print("=" * 70)
print(f"Updated sessions: {updated_count}")
print(f"Total tokens: {total_tokens:,}")
print(f"Average tokens per session: {total_tokens // updated_count if updated_count > 0 else 0:,}")
print("=" * 70)
