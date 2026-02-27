# test_hook.py - 测试 Hook 功能
import sys
sys.path.insert(0, r'C:\Users\34438\.openclaw\hooks')

try:
    import observational_memory
    
    print("=" * 50)
    print("Testing Observational Memory Hook")
    print("=" * 50)
    
    # 测试消息记录
    print("\n[1/2] Testing on_message...")
    observational_memory.on_message({
        'session_id': 'test-hook-001',
        'message': 'This is a test message from hook test',
        'role': 'user'
    })
    
    print("\n[2/2] Testing on_session_end...")
    observational_memory.on_session_end({
        'session_id': 'test-hook-001'
    })
    
    print("\n" + "=" * 50)
    print("Hook test completed")
    print("=" * 50)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
