"""
Stress test for observational_memory_threaded.py

Tests with 100+ concurrent sessions to verify scalability.
"""

import sys
from pathlib import Path
import tempfile
import shutil
import time

sys.path.insert(0, str(Path(__file__).parent))

from observational_memory_threaded import (
    ThreadSafeObservationExtractor,
    BatchProcessor
)


def stress_test_100_sessions():
    """压力测试：100 个并发会话"""
    print("=== Stress Test: 100 Concurrent Sessions ===\n")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        extractor = ThreadSafeObservationExtractor(temp_dir, max_workers=20)
        
        # 创建 100 个会话
        sessions = {}
        for i in range(100):
            sessions[f'stress_session_{i}'] = [
                {'role': 'user', 'content': f'用户消息 {i}: 我在做项目', 'timestamp': '2026-02-27T10:00:00'},
                {'role': 'assistant', 'content': f'助手回复 {i}: 很好！', 'timestamp': '2026-02-27T10:00:01'},
                {'role': 'user', 'content': f'用户消息 {i}: 完成了功能', 'timestamp': '2026-02-27T10:00:02'},
                {'role': 'assistant', 'content': f'助手回复 {i}: 恭喜！', 'timestamp': '2026-02-27T10:00:03'}
            ]
        
        print(f"Created {len(sessions)} sessions")
        print("Starting concurrent processing...\n")
        
        start_time = time.time()
        results = extractor.process_sessions_concurrent(sessions)
        duration = time.time() - start_time
        
        # 统计
        success_count = sum(1 for r in results if r.success)
        failed_count = sum(1 for r in results if not r.success)
        avg_duration = sum(r.duration for r in results) / len(results)
        max_duration = max(r.duration for r in results)
        min_duration = min(r.duration for r in results)
        
        print(f"Total time: {duration:.3f}s")
        print(f"Success: {success_count}/{len(results)}")
        print(f"Failed: {failed_count}/{len(results)}")
        print(f"Avg per session: {avg_duration:.3f}s")
        print(f"Max duration: {max_duration:.3f}s")
        print(f"Min duration: {min_duration:.3f}s")
        print(f"Throughput: {len(results)/duration:.2f} sessions/s")
        
        # 验证性能要求
        if avg_duration < 1.0:
            print("\n✓ PASS: Performance requirement met (< 1s per session)")
        else:
            print(f"\n✗ FAIL: Performance requirement not met ({avg_duration:.3f}s > 1s)")
        
        if success_count == len(results):
            print("✓ PASS: All sessions processed successfully")
        else:
            print(f"✗ FAIL: {failed_count} sessions failed")
        
        extractor.shutdown()
        
        return success_count == len(results) and avg_duration < 1.0
        
    finally:
        shutil.rmtree(temp_dir)


def stress_test_500_sessions():
    """压力测试：500 个会话（批量处理）"""
    print("\n=== Stress Test: 500 Sessions (Batch Processing) ===\n")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        processor = BatchProcessor(temp_dir, max_workers=20, batch_size=100)
        
        # 创建 500 个会话
        sessions = {}
        for i in range(500):
            sessions[f'batch_session_{i}'] = [
                {'role': 'user', 'content': f'批量测试 {i}', 'timestamp': '2026-02-27T10:00:00'},
                {'role': 'assistant', 'content': f'回复 {i}', 'timestamp': '2026-02-27T10:00:01'}
            ]
        
        print(f"Created {len(sessions)} sessions")
        print("Starting batch processing...\n")
        
        start_time = time.time()
        summary = processor.process_all_sessions(sessions, show_progress=True)
        duration = time.time() - start_time
        
        print(f"\nTotal time: {duration:.3f}s")
        print(f"Success: {summary['success']}/{summary['total']}")
        print(f"Failed: {summary['failed']}/{summary['total']}")
        print(f"Avg per session: {summary['avg_duration']:.3f}s")
        print(f"Throughput: {summary['total']/duration:.2f} sessions/s")
        
        if summary['success'] == summary['total']:
            print("\n✓ PASS: All sessions processed successfully")
        else:
            print(f"\n✗ FAIL: {summary['failed']} sessions failed")
            print(f"Errors: {summary['errors'][:5]}")  # 显示前 5 个错误
        
        processor.shutdown()
        
        return summary['success'] == summary['total']
        
    finally:
        shutil.rmtree(temp_dir)


def concurrent_read_write_test():
    """并发读写测试"""
    print("\n=== Concurrent Read/Write Test ===\n")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        extractor = ThreadSafeObservationExtractor(temp_dir, max_workers=10)
        
        # 先写入一些数据
        for i in range(10):
            extractor._save_observations_safe(f'session_{i}', f'Initial content {i}')
        
        print("Initial data written")
        
        # 并发读写
        import threading
        import random
        
        results = {'read': 0, 'write': 0, 'errors': 0}
        results_lock = threading.Lock()
        
        def read_operation():
            try:
                session_id = f'session_{random.randint(0, 9)}'
                content = extractor._load_observations_safe(session_id)
                with results_lock:
                    results['read'] += 1
            except Exception as e:
                with results_lock:
                    results['errors'] += 1
        
        def write_operation():
            try:
                session_id = f'session_{random.randint(0, 9)}'
                content = f'Updated content {random.randint(0, 1000)}'
                extractor._save_observations_safe(session_id, content)
                with results_lock:
                    results['write'] += 1
            except Exception as e:
                with results_lock:
                    results['errors'] += 1
        
        # 创建 50 个读线程和 50 个写线程
        threads = []
        for i in range(50):
            threads.append(threading.Thread(target=read_operation))
            threads.append(threading.Thread(target=write_operation))
        
        print("Starting 100 concurrent read/write operations...")
        
        start_time = time.time()
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        duration = time.time() - start_time
        
        print(f"\nCompleted in {duration:.3f}s")
        print(f"Read operations: {results['read']}")
        print(f"Write operations: {results['write']}")
        print(f"Errors: {results['errors']}")
        
        if results['errors'] == 0:
            print("\n✓ PASS: No errors in concurrent read/write")
        else:
            print(f"\n✗ FAIL: {results['errors']} errors occurred")
        
        extractor.shutdown()
        
        return results['errors'] == 0
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    print("Observational Memory - Stress Tests\n")
    print("="*60)
    
    all_passed = True
    
    try:
        all_passed &= stress_test_100_sessions()
    except Exception as e:
        print(f"\n✗ 100 Sessions Test FAILED: {e}")
        all_passed = False
    
    try:
        all_passed &= stress_test_500_sessions()
    except Exception as e:
        print(f"\n✗ 500 Sessions Test FAILED: {e}")
        all_passed = False
    
    try:
        all_passed &= concurrent_read_write_test()
    except Exception as e:
        print(f"\n✗ Concurrent Read/Write Test FAILED: {e}")
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL STRESS TESTS PASSED")
    else:
        print("✗ SOME STRESS TESTS FAILED")
    print("="*60)
