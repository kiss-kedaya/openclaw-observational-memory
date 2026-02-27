import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

cursor.execute("SELECT content FROM observations WHERE session_id = 'test-chinese-20260227195756' LIMIT 1")
row = cursor.fetchone()

if row:
    content_bytes = row[0].encode('utf-8')
    # 正确解码
    content_decoded = content_bytes.decode('utf-8')
    print(f"Decoded content: {content_decoded}")
    
    # 验证
    expected = "这是一个中文测试消息，用于验证UTF-8编码是否正常工作。"
    if content_decoded == expected:
        print("\nSUCCESS: 数据库存储的中文完全正确！")
    else:
        print(f"\nExpected: {expected}")
        print(f"Got: {content_decoded}")

conn.close()
