"""
Unit tests for observational_memory_threaded.py

Tests:
- Thread safety of file I/O
- Concurrent session processing
- Lock mechanism
- Performance benchmarks
- Error handling

Author: Full-Stack Architect
Date: 2026-02-27
"""

import pytest
import time
import threading
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from observational_memory_threaded import (
    ThreadSafeObservationExtractor,
    BatchProcessor,
    ProcessingResult
)


@pytest.fixture
def temp_workspace():
    """创建临时工作目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_sessions():
    """创建示例会话数据"""
    sessions = {}
    for i in range(20):
        sessions[f'session_{i}'] = [
            {
                'role': 'user',
                'content': f'用户消息 {i}: 我喜欢编程',
                'timestamp': '2026-02-27T10:00:00'
            },
            {
                'role': 'assistant',
                'content': f'助手回复 {i}: 很高兴听到你喜欢编程！',
                'timestamp': '2026-02-27T10:00:01'
            },
            {
                'role': 'user',
                'content': f'用户消息 {i}: 我完成了项目',
                'timestamp': '2026-02-27T10:00:02'
            }
        ]
    return sessions


class TestThreadSafeObservationExtractor:
    """测试线程安全的观察提取器"""
    
    def test_initialization(self, temp_workspace):
        """测试初始化"""
        extractor = ThreadSafeObservationExtractor(temp_workspace, max_workers=5)
        
        assert extractor.workspace_dir == temp_workspace
        assert extractor.observations_dir.exists()
        assert extractor.executor._max_workers == 5
        assert len(extractor.file_locks) == 0
    
    def test_file_lock_creation(self, temp_workspace):
        """测试文件锁创建"""
        extractor = ThreadSafeObservationExtractor(temp_workspace)
        
        lock1 = extractor._get_file_lock('session_1')
        lock2 = extractor._get_file_lock('session_1')
        lock3 = extractor._get_file_lock('session_2')
        
        # 同一个 session_id 应该返回同一个锁
        assert lock1 is lock2
        # 不同 session_id 应该返回不同的锁
        assert lock1 is not lock3
    
    def test_save_and_load_observations(self, temp_workspace):
        """测试保存和加载观察"""
        extractor = ThreadSafeObservationExtractor(temp_workspace)
        
        session_id = 'test_session'
        observations = '* 🔴 (10:00) 用户喜欢编程\n* 🟡 (10:01) 项目已完成'
        
        # 保存
        extractor._save_observations_safe(session_id, observations)
        
        # 加载
        loaded = extractor._load_observations_safe(session_id)
        assert loaded == observations
        
        # 加载不存在的会话
        not_found = extractor._load_observations_safe('non_existent')
        assert not_found is None
    
    def test_concurrent_save_same_session(self, temp_workspace):
        """测试并发保存同一个会话（锁机制）"""
        extractor = ThreadSafeObservationExtractor(temp_workspace)
        session_id = 'concurrent_session'
        
        results = []
        errors = []
        
        def save_observation(content: str):
            try:
                extractor._save_observations_safe(session_id, content)
                results.append(content)
            except Exception as e:
                errors.append(str(e))
        
        # 创建 10 个线程同时写入
        threads = []
        for i in range(10):
            t = threading.Thread(target=save_observation, args=(f'Observation {i}',))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 应该没有错误
        assert len(errors) == 0
        # 应该有 10 次写入
        assert len(results) == 10
        
        # 最终文件应该包含最后一次写入的内容
        final_content = extractor._load_observations_safe(session_id)
        assert final_content in results
    
    def test_process_single_session(self, temp_workspace):
        """测试处理单个会话"""
        extractor = ThreadSafeObservationExtractor(temp_workspace)
        
        messages = [
            {'role': 'user', 'content': '我喜欢编程', 'timestamp': '2026-02-27T10:00:00'},
            {'role': 'assistant', 'content': '很好！', 'timestamp': '2026-02-27T10:00:01'}
        ]
        
        result = extractor._process_single_session('test_session', messages)
        
        assert result.success is True
        assert result.session_id == 'test_session'
        assert result.observations is not None
        assert result.token_count > 0
        assert result.duration > 0
    
    def test_process_sessions_concurrent(self, temp_workspace, sample_sessions):
        """测试并发处理多个会话"""
        extractor = ThreadSafeObservationExtractor(temp_workspace, max_workers=5)
        
        # 进度跟踪
        progress_updates = []
        
        def progress_callback(current, total):
            progress_updates.append((current, total))
        
        # 并发处理
        results = extractor.process_sessions_concurrent(sample_sessions, progress_callback)
        
        # 验证结果
        assert len(results) == len(sample_sessions)
        assert all(r.success for r in results)
        assert len(progress_updates) == len(sample_sessions)
        
        # 验证统计信息
        stats = extractor.get_stats()
        assert stats['total'] == len(sample_sessions)
        assert stats['success'] == len(sample_sessions)
        assert stats['failed'] == 0
        assert 'duration' in stats
        assert 'throughput' in stats
        
        extractor.shutdown()
    
    def test_performance_benchmark(self, temp_workspace, sample_sessions):
        """性能基准测试：10+ 并发会话"""
        extractor = ThreadSafeObservationExtractor(temp_workspace, max_workers=10)
        
        start_time = time.time()
        results = extractor.process_sessions_concurrent(sample_sessions)
        duration = time.time() - start_time
        
        # 验证性能
        assert len(results) == 20
        assert all(r.success for r in results)
        
        # 平均每个会话处理时间应该 < 1s
        avg_duration = sum(r.duration for r in results) / len(results)
        assert avg_duration < 1.0, f"Average duration {avg_duration:.3f}s exceeds 1s"
        
        # 总处理时间应该远小于串行处理时间
        serial_time_estimate = avg_duration * len(results)
        speedup = serial_time_estimate / duration
        assert speedup > 2, f"Speedup {speedup:.2f}x is too low"
        
        print(f"\n=== Performance Benchmark ===")
        print(f"Sessions: {len(results)}")
        print(f"Total time: {duration:.3f}s")
        print(f"Avg per session: {avg_duration:.3f}s")
        print(f"Speedup: {speedup:.2f}x")
        
        extractor.shutdown()
    
    def test_error_handling(self, temp_workspace):
        """测试错误处理"""
        extractor = ThreadSafeObservationExtractor(temp_workspace)
        
        # 无效的消息格式
        invalid_messages = [
            {'invalid': 'data'}
        ]
        
        result = extractor._process_single_session('error_session', invalid_messages)
        
        # 应该捕获错误而不是崩溃
        assert result.success is False
        assert result.error is not None
        assert result.duration > 0
        
        extractor.shutdown()


class TestBatchProcessor:
    """测试批量处理器"""
    
    def test_initialization(self, temp_workspace):
        """测试初始化"""
        processor = BatchProcessor(temp_workspace, max_workers=5, batch_size=50)
        
        assert processor.workspace_dir == temp_workspace
        assert processor.max_workers == 5
        assert processor.batch_size == 50
    
    def test_process_all_sessions(self, temp_workspace, sample_sessions):
        """测试处理所有会话"""
        processor = BatchProcessor(temp_workspace, max_workers=5, batch_size=10)
        
        summary = processor.process_all_sessions(sample_sessions, show_progress=False)
        
        assert summary['total'] == len(sample_sessions)
        assert summary['success'] == len(sample_sessions)
        assert summary['failed'] == 0
        assert summary['avg_duration'] > 0
        assert len(summary['errors']) == 0
        
        processor.shutdown()
    
    def test_batch_processing(self, temp_workspace):
        """测试分批处理"""
        # 创建 150 个会话
        large_sessions = {}
        for i in range(150):
            large_sessions[f'session_{i}'] = [
                {'role': 'user', 'content': f'Message {i}', 'timestamp': '2026-02-27T10:00:00'}
            ]
        
        processor = BatchProcessor(temp_workspace, max_workers=10, batch_size=50)
        summary = processor.process_all_sessions(large_sessions, show_progress=False)
        
        # 应该分 3 批处理（150 / 50 = 3）
        assert summary['total'] == 150
        assert summary['success'] == 150
        
        processor.shutdown()


class TestThreadSafety:
    """线程安全性测试"""
    
    def test_concurrent_access_different_sessions(self, temp_workspace):
        """测试并发访问不同会话（无锁竞争）"""
        extractor = ThreadSafeObservationExtractor(temp_workspace, max_workers=10)
        
        def process_session(session_id: str):
            messages = [
                {'role': 'user', 'content': f'Content for {session_id}', 'timestamp': '2026-02-27T10:00:00'}
            ]
            return extractor._process_single_session(session_id, messages)
        
        # 创建 20 个线程处理不同会话
        threads = []
        results = []
        
        for i in range(20):
            t = threading.Thread(target=lambda i=i: results.append(process_session(f'session_{i}')))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 所有会话都应该成功
        assert len(results) == 20
        assert all(r.success for r in results)
        
        extractor.shutdown()
    
    def test_stress_test(self, temp_workspace):
        """压力测试：100 个并发会话"""
        extractor = ThreadSafeObservationExtractor(temp_workspace, max_workers=20)
        
        sessions = {}
        for i in range(100):
            sessions[f'stress_session_{i}'] = [
                {'role': 'user', 'content': f'Stress test {i}', 'timestamp': '2026-02-27T10:00:00'}
            ]
        
        start_time = time.time()
        results = extractor.process_sessions_concurrent(sessions)
        duration = time.time() - start_time
        
        assert len(results) == 100
        assert all(r.success for r in results)
        
        print(f"\n=== Stress Test ===")
        print(f"Sessions: 100")
        print(f"Duration: {duration:.3f}s")
        print(f"Throughput: {100/duration:.2f} sessions/s")
        
        extractor.shutdown()


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
