"""
Quick validation test for observational_memory_threaded.py

Runs basic functionality tests without pytest.
"""

import sys
from pathlib import Path
import tempfile
import shutil
import time

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from observational_memory_threaded import (
    ThreadSafeObservationExtractor,
    BatchProcessor
)

def test_basic_functionality():
    """基础功能测试"""
    print("=== Test 1: Basic Functionality ===")
    
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # 创建提取器
        extractor = ThreadSafeObservationExtractor(temp_dir, max_workers=5)
        print("✓ Extractor created")
        
        # 创建测试会话
        sessions = {}
        for i in range(10):
            sessions[f'session_{i}'] = [
                {'role': 'user', 'content': f'我喜欢编程 {i}', 'timestamp': '2026-02-27T10:00:00'},
                {'role': 'assistant', 'content': f'很好！{i}', 'timestamp': '2026-02-27T10:00:01'}
            ]
        print(f"✓ Created {len(sessions)} test sessions")
        
        # 并发处理
        start_time = time.time()
        results = extractor.process_sessions_concurrent(sessions)
        duration = time.time() - start_time
        
        print(f"✓ Processed {len(results)} sessions in {duration:.3f}s")
        
        # 验证结果
        success_count = sum(1 for r in results if r.success)
        print(f"✓ Success: {success_count}/{len(results)}")
        
        # 获取统计
        stats = extractor.get_stats()
        print(f"✓ Stats: {stats['success']} success, {stats['failed']} failed")
        print(f"✓ Throughput: {stats.get('throughput', 0):.2f} sessions/s")
        
        extractor.shutdown()
        print("✓ Extractor shutdown")
        
        return True
        
    finally:
        # 清理
        shutil.rmtree(temp_dir)
        print("✓ Cleanup complete")


def test_performance():
    """性能测试"""
    print("\n=== Test 2: Performance (20 concurrent sessions) ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        extractor = ThreadSafeObservationExtractor(temp_dir, max_workers=10)
        
        # 创建 20 个会话
        sessions = {}
        for i in range(20):
            sessions[f'perf_session_{i}'] = [
                {'role': 'user', 'content': f'性能测试 {i}', 'timestamp': '2026-02-27T10:00:00'},
                {'role': 'assistant', 'content': f'回复 {i}', 'timestamp': '2026-02-27T10:00:01'},
                {'role': 'user', 'content': f'完成任务 {i}', 'timestamp': '2026-02-27T10:00:02'}
            ]
        
        start_time = time.time()
        results = extractor.process_sessions_concurrent(sessions)
        duration = time.time() - start_time
        
        avg_duration = sum(r.duration for r in results) / len(results)
        
        print(f"✓ Total time: {duration:.3f}s")
        print(f"✓ Avg per session: {avg_duration:.3f}s")
        print(f"✓ All sessions < 1s: {all(r.duration < 1.0 for r in results)}")
        
        # 验证性能要求
        if avg_duration < 1.0:
            print("✓ PASS: Performance requirement met (< 1s per session)")
        else:
            print(f"✗ FAIL: Performance requirement not met ({avg_duration:.3f}s > 1s)")
        
        extractor.shutdown()
        return avg_duration < 1.0
        
    finally:
        shutil.rmtree(temp_dir)


def test_batch_processor():
    """批量处理器测试"""
    print("\n=== Test 3: Batch Processor ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        processor = BatchProcessor(temp_dir, max_workers=5, batch_size=10)
        
        # 创建 25 个会话（应该分 3 批）
        sessions = {}
        for i in range(25):
            sessions[f'batch_session_{i}'] = [
                {'role': 'user', 'content': f'批量测试 {i}', 'timestamp': '2026-02-27T10:00:00'}
            ]
        
        summary = processor.process_all_sessions(sessions, show_progress=False)
        
        print(f"✓ Total: {summary['total']}")
        print(f"✓ Success: {summary['success']}")
        print(f"✓ Failed: {summary['failed']}")
        print(f"✓ Avg duration: {summary['avg_duration']:.3f}s")
        
        processor.shutdown()
        
        return summary['success'] == 25
        
    finally:
        shutil.rmtree(temp_dir)


def test_thread_safety():
    """线程安全测试"""
    print("\n=== Test 4: Thread Safety ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        extractor = ThreadSafeObservationExtractor(temp_dir, max_workers=10)
        
        # 测试文件锁
        lock1 = extractor._get_file_lock('session_1')
        lock2 = extractor._get_file_lock('session_1')
        lock3 = extractor._get_file_lock('session_2')
        
        assert lock1 is lock2, "Same session should return same lock"
        assert lock1 is not lock3, "Different sessions should return different locks"
        print("✓ File lock mechanism working")
        
        # 测试并发写入同一文件
        import threading
        results = []
        
        def save_test(content):
            extractor._save_observations_safe('concurrent_test', content)
            results.append(content)
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=save_test, args=(f'Content {i}',))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print(f"✓ Concurrent writes completed: {len(results)} writes")
        
        # 验证文件内容
        final_content = extractor._load_observations_safe('concurrent_test')
        assert final_content in results, "Final content should be one of the writes"
        print("✓ Thread-safe file I/O verified")
        
        extractor.shutdown()
        return True
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    print("Observational Memory - Thread-Safe Implementation Tests\n")
    
    all_passed = True
    
    try:
        all_passed &= test_basic_functionality()
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        all_passed = False
    
    try:
        all_passed &= test_performance()
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        all_passed = False
    
    try:
        all_passed &= test_batch_processor()
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        all_passed = False
    
    try:
        all_passed &= test_thread_safety()
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*50)
