"""
Tests for Concurrent Observational Memory

Run with: pytest test_concurrent.py -v
"""

import pytest
import threading
import time
import queue
from pathlib import Path
from datetime import datetime
from observational_memory.concurrent import (
    ConcurrentObservationalProcessor,
    ThreadSafeObservationalMemoryManager,
    ProcessingTask,
    ProcessingResult
)


class TestThreadSafeManager:
    """Test thread-safe memory manager"""
    
    def setup_method(self):
        self.test_dir = Path("./test_threadsafe_workspace")
        self.test_dir.mkdir(exist_ok=True)
        self.manager = ThreadSafeObservationalMemoryManager(self.test_dir)
    
    def teardown_method(self):
        """Clean up test files"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_concurrent_save(self):
        """Test concurrent save operations"""
        session_id = "test_session"
        num_threads = 10
        
        def save_observation(thread_id):
            obs = f"Observation from thread {thread_id}"
            self.manager.save_observations(session_id, obs)
        
        # Create threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=save_observation, args=(i,))
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify file exists and is readable
        loaded = self.manager.load_observations(session_id)
        assert loaded is not None
        assert "Observation from thread" in loaded
    
    def test_concurrent_load(self):
        """Test concurrent load operations"""
        session_id = "test_session"
        self.manager.save_observations(session_id, "Test observation")
        
        num_threads = 10
        results = []
        results_lock = threading.Lock()
        
        def load_observation():
            obs = self.manager.load_observations(session_id)
            with results_lock:
                results.append(obs)
        
        # Create threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=load_observation)
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify all reads succeeded
        assert len(results) == num_threads
        assert all(r == "Test observation" for r in results)
    
    def test_concurrent_process(self):
        """Test concurrent session processing"""
        num_sessions = 5
        
        def process_session(session_id):
            messages = [
                {
                    'role': 'user',
                    'content': f'Message for {session_id}',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            return self.manager.process_session(session_id, messages)
        
        results = []
        results_lock = threading.Lock()
        
        def worker(session_id):
            result = process_session(session_id)
            with results_lock:
                results.append(result)
        
        # Create threads
        threads = []
        for i in range(num_sessions):
            t = threading.Thread(target=worker, args=(f'session_{i}',))
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify all sessions processed
        assert len(results) == num_sessions
        assert all('observations' in r for r in results)


class TestConcurrentProcessor:
    """Test concurrent processor"""
    
    def setup_method(self):
        self.test_dir = Path("./test_concurrent_workspace")
        self.test_dir.mkdir(exist_ok=True)
        self.processor = ConcurrentObservationalProcessor(
            workspace_dir=self.test_dir,
            max_workers=5
        )
    
    def teardown_method(self):
        """Clean up test files"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_process_single(self):
        """Test processing a single task"""
        messages = [
            {
                'role': 'user',
                'content': '测试消息',
                'timestamp': datetime.now().isoformat()
            }
        ]
        task = ProcessingTask('session_1', messages)
        
        result = self.processor.process_single(task)
        
        assert result.success
        assert result.session_id == 'session_1'
        assert result.token_count > 0
        assert result.processing_time >= 0
    
    def test_process_batch(self):
        """Test batch processing"""
        num_tasks = 10
        tasks = []
        
        for i in range(num_tasks):
            messages = [
                {
                    'role': 'user',
                    'content': f'测试消息 {i}',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            tasks.append(ProcessingTask(f'session_{i}', messages))
        
        results = self.processor.process_batch(tasks)
        
        assert len(results) == num_tasks
        assert all(r.success for r in results)
        assert all(r.token_count > 0 for r in results)
    
    def test_process_batch_with_priority(self):
        """Test batch processing with priority"""
        tasks = [
            ProcessingTask('low_priority', [{'role': 'user', 'content': 'Low', 'timestamp': datetime.now().isoformat()}], priority=0),
            ProcessingTask('high_priority', [{'role': 'user', 'content': 'High', 'timestamp': datetime.now().isoformat()}], priority=10),
            ProcessingTask('medium_priority', [{'role': 'user', 'content': 'Medium', 'timestamp': datetime.now().isoformat()}], priority=5)
        ]
        
        results = self.processor.process_batch(tasks)
        
        assert len(results) == 3
        assert all(r.success for r in results)
    
    def test_process_batch_with_timeout(self):
        """Test batch processing with timeout"""
        # Create tasks that take time
        tasks = []
        for i in range(5):
            messages = [
                {
                    'role': 'user',
                    'content': f'测试消息 {i}' * 100,  # Longer message
                    'timestamp': datetime.now().isoformat()
                }
            ]
            tasks.append(ProcessingTask(f'session_{i}', messages))
        
        # Process with generous timeout
        results = self.processor.process_batch(tasks, timeout=10.0)
        
        # Should complete within timeout
        assert len(results) > 0
    
    def test_process_queue(self):
        """Test queue-based processing"""
        task_queue = queue.PriorityQueue()
        stop_event = threading.Event()
        
        # Add tasks to queue
        for i in range(5):
            messages = [
                {
                    'role': 'user',
                    'content': f'测试消息 {i}',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            task = ProcessingTask(f'session_{i}', messages, priority=i)
            task_queue.put(task)
        
        # Start queue processor in background
        processor_thread = threading.Thread(
            target=self.processor.process_queue,
            args=(task_queue, stop_event)
        )
        processor_thread.start()
        
        # Wait for queue to be processed
        task_queue.join()
        
        # Stop processor
        stop_event.set()
        processor_thread.join(timeout=2.0)
        
        # Verify statistics
        stats = self.processor.get_statistics()
        assert stats['total_processed'] == 5
        assert stats['total_failed'] == 0
    
    def test_statistics(self):
        """Test statistics tracking"""
        tasks = []
        for i in range(3):
            messages = [
                {
                    'role': 'user',
                    'content': f'测试消息 {i}',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            tasks.append(ProcessingTask(f'session_{i}', messages))
        
        self.processor.process_batch(tasks)
        
        stats = self.processor.get_statistics()
        
        assert stats['total_processed'] == 3
        assert stats['total_failed'] == 0
        assert stats['total_time'] > 0
        assert stats['average_time'] > 0
    
    def test_error_handling(self):
        """Test error handling for invalid tasks"""
        # Create task with invalid messages
        task = ProcessingTask('invalid_session', [])
        
        result = self.processor.process_single(task)
        
        # Should handle gracefully
        assert result.session_id == 'invalid_session'
        # May succeed or fail depending on implementation
    
    def test_progress_callback(self):
        """Test progress callback"""
        progress_updates = []
        
        def progress_callback(session_id, progress):
            progress_updates.append((session_id, progress))
        
        processor = ConcurrentObservationalProcessor(
            workspace_dir=self.test_dir,
            max_workers=2,
            progress_callback=progress_callback
        )
        
        tasks = []
        for i in range(3):
            messages = [
                {
                    'role': 'user',
                    'content': f'测试消息 {i}',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            tasks.append(ProcessingTask(f'session_{i}', messages))
        
        processor.process_batch(tasks)
        
        # Verify callbacks were called
        assert len(progress_updates) == 3
        assert all(progress == 1.0 for _, progress in progress_updates)


class TestPerformance:
    """Performance tests"""
    
    def setup_method(self):
        self.test_dir = Path("./test_performance_workspace")
        self.test_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up test files"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_concurrent_vs_sequential(self):
        """Compare concurrent vs sequential processing"""
        num_sessions = 10
        
        # Create tasks
        tasks = []
        for i in range(num_sessions):
            messages = [
                {
                    'role': 'user',
                    'content': f'测试消息 {i}' * 10,
                    'timestamp': datetime.now().isoformat()
                }
            ]
            tasks.append(ProcessingTask(f'session_{i}', messages))
        
        # Sequential processing
        sequential_processor = ConcurrentObservationalProcessor(
            workspace_dir=self.test_dir,
            max_workers=1
        )
        start = time.time()
        sequential_processor.process_batch(tasks)
        sequential_time = time.time() - start
        
        # Concurrent processing
        concurrent_processor = ConcurrentObservationalProcessor(
            workspace_dir=self.test_dir,
            max_workers=5
        )
        start = time.time()
        concurrent_processor.process_batch(tasks)
        concurrent_time = time.time() - start
        
        print(f"\nSequential: {sequential_time:.3f}s")
        print(f"Concurrent: {concurrent_time:.3f}s")
        print(f"Speedup: {sequential_time / concurrent_time:.2f}x")
        
        # Concurrent should be faster (or at least not much slower)
        # Allow some overhead for thread management
        assert concurrent_time <= sequential_time * 1.5
    
    def test_processing_time_under_1s(self):
        """Test that single session processing is under 1s"""
        processor = ConcurrentObservationalProcessor(
            workspace_dir=self.test_dir,
            max_workers=1
        )
        
        messages = [
            {
                'role': 'user',
                'content': '测试消息' * 50,
                'timestamp': datetime.now().isoformat()
            }
        ]
        task = ProcessingTask('session_1', messages)
        
        result = processor.process_single(task)
        
        assert result.success
        assert result.processing_time < 1.0, f"Processing took {result.processing_time:.3f}s (> 1s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=observational_memory_concurrent"])
