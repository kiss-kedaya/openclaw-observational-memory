import sqlite3

print("Clearing database...")

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

# 清空所有数据
cursor.execute("DELETE FROM messages")
cursor.execute("DELETE FROM observations")
cursor.execute("DELETE FROM sessions")

conn.commit()
conn.close()

print("Database cleared!")
