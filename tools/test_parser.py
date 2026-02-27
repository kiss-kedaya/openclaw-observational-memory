import sys
sys.path.insert(0, '.')
from session_poller import parse_session_file
from pathlib import Path

# 测试解析一个文件
test_file = Path("C:/Users/34438/.openclaw/agents/main/sessions/025d36f8-f070-4af9-8598-14367dc046a6.jsonl")

print(f"Testing: {test_file.name}")
print()

messages = parse_session_file(test_file)

print(f"Parsed {len(messages)} messages")
print()

if messages:
    print("First 3 messages:")
    for i, msg in enumerate(messages[:3], 1):
        print(f"\n[{i}] Role: {msg['role']}")
        print(f"Length: {len(msg['content'])} chars")
        print(f"Preview: {msg['content'][:150]}...")
