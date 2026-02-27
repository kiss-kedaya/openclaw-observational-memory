# test_hook_integration.py - 测试 Hook 集成
import sys
sys.path.insert(0, r'C:\Users\34438\.openclaw\hooks')

import observational_memory
import json

# 模拟 OpenClaw 事件
test_event = {
    'session_id': 'test-integration-001',
    'message': 'This is a test message to verify hook integration',
    'role': 'user',
    'timestamp': '2026-02-27T09:13:00Z'
}

print("=" * 60)
print("Testing Observational Memory Hook Integration")
print("=" * 60)
print()
print("Test Event:")
print(json.dumps(test_event, indent=2))
print()

# 测试 on_message
print("[1/2] Testing on_message...")
observational_memory.on_message(test_event)
print()

# 测试 on_session_end
print("[2/2] Testing on_session_end...")
observational_memory.on_session_end({'session_id': test_event['session_id']})
print()

print("=" * 60)
print("Test completed")
print("=" * 60)
