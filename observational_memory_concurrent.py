"""
Observational Memory - Concurrent Processing Extension

Adds multi-threading support for processing multiple sessions concurrently.

Features:
- Thread-safe file operations
- Concurrent session processing (10+ sessions)
- Progress tracking and error handling
- Graceful shutdown

Author: OpenClaw Community
License: MIT
"""

import threading
import queue
import logging
from typing import List, Dict, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass
from datetime import datetime
import time

from observational_memory import ObservationalMemoryManager, ObservationExtractor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingTask:
    """Represents a session processing task"""
    session_id: str
    messages: List[Dict]
    priority: int = 0  # Higher = more urgent
    
    def __lt__(self, other):
        """For priority queue sorting"""
        return self.priority > other.priority


@dataclass
class ProcessingResult:
    """Result of processing a session"""
    session_id: str
    success: bool
    observations: Optional[str] = None
    compressed: Optional[str] = None
    token_count: int = 0
    compressed_token_count: int = 0
    error: Optional[str] = None
    processing_time: float = 0.0


class ThreadSafeObservationalMemoryManager(ObservationalMemoryManager):
    """
    Thread-safe version of ObservationalMemoryManager
    
    Uses file locks to prevent concurrent write conflicts.
    """
    
    def __init__(self, workspace_dir: Path):
        super().__init__(workspace_dir)
        self._file_locks = {}
        self._locks_lock = threading.RLock()
    
    def _get_file_lock(self, session_id: str) -> threading.Lock:
        """Get or create a lock for a specific session file"""
        with self._locks_lock:
            if session_id not in self._file_locks:
                self._file_locks[session_id] = threading.RLock()
            return self._file_locks[session_id]
    
    def save_observations(self, session_id: str, observations: str):
        """Thread-safe save observations"""
        lock = self._get_file_lock(session_id)
        with lock:
            super().save_observations(session_id, observations)
            logger.debug(f"Saved observations for session {session_id}")
    
    def load_observations(self, session_id: str) -> Optional[str]:
        """Thread-safe load observations"""
        lock = self._get_file_lock(session_id)
        with lock:
            return super().load_observations(session_id)
    
    def process_session(self, session_id: str, messages: List[Dict]) -> Dict:
        """Thread-safe process session"""
        lock = self._get_file_lock(session_id)
        with lock:
            return super().process_session(session_id, messages)


class ConcurrentObservationalProcessor:
    """
    Concurrent processor for observational memory
    
    Processes multiple sessions in parallel using a thread pool.
    Supports priority queuing, progress tracking, and error handling.
    
    Example:
        processor = ConcurrentObservationalProcessor(
            workspace_dir=Path.cwd(),
            max_workers=10
        )
        
        tasks = [
            ProcessingTask("session_1", messages_1),
            ProcessingTask("session_2", messages_2, priority=1)
        ]
        
        results = processor.process_batch(tasks)
        for result in results:
            if result.success:
                print(f"Processed {result.session_id}: {result.token_count} tokens")
    """
    
    def __init__(
        self,
        workspace_dir: Path,
        max_workers: int = 10,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        """
        Initialize concurrent processor
        
        Args:
            workspace_dir: Workspace directory for memory storage
            max_workers: Maximum number of concurrent workers
            progress_callback: Optional callback for progress updates
                               Signature: callback(session_id: str, progress: float)
        """
        self.workspace_dir = workspace_dir
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        
        # Thread-safe manager
        self.manager = ThreadSafeObservationalMemoryManager(workspace_dir)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'total_failed': 0,
            'total_time': 0.0
        }
        self.stats_lock = threading.RLock()
        
        logger.info(f"Initialized ConcurrentObservationalProcessor with {max_workers} workers")
    
    def process_single(self, task: ProcessingTask) -> ProcessingResult:
        """
        Process a single session
        
        Args:
            task: Processing task
        
        Returns:
            Processing result
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing session {task.session_id} (priority={task.priority})")
            
            # Process session
            result = self.manager.process_session(task.session_id, task.messages)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            with self.stats_lock:
                self.stats['total_processed'] += 1
                self.stats['total_time'] += processing_time
            
            # Progress callback
            if self.progress_callback:
                self.progress_callback(task.session_id, 1.0)
            
            logger.info(
                f"Completed session {task.session_id} in {processing_time:.2f}s "
                f"({result['token_count']} tokens)"
            )
            
            return ProcessingResult(
                session_id=task.session_id,
                success=True,
                observations=result['observations'],
                compressed=result['compressed'],
                token_count=result['token_count'],
                compressed_token_count=result['compressed_token_count'],
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Update statistics
            with self.stats_lock:
                self.stats['total_failed'] += 1
            
            logger.error(f"Failed to process session {task.session_id}: {e}", exc_info=True)
            
            return ProcessingResult(
                session_id=task.session_id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    def process_batch(
        self,
        tasks: List[ProcessingTask],
        timeout: Optional[float] = None
    ) -> List[ProcessingResult]:
        """
        Process multiple sessions concurrently
        
        Args:
            tasks: List of processing tasks
            timeout: Optional timeout in seconds for the entire batch
        
        Returns:
            List of processing results (in completion order)
        """
        if not tasks:
            return []
        
        logger.info(f"Starting batch processing of {len(tasks)} sessions")
        batch_start = time.time()
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.process_single, task): task
                for task in tasks
            }
            
            # Collect results as they complete
            try:
                for future in as_completed(future_to_task, timeout=timeout):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Unexpected error for task {task.session_id}: {e}")
                        results.append(ProcessingResult(
                            session_id=task.session_id,
                            success=False,
                            error=f"Unexpected error: {e}"
                        ))
            
            except TimeoutError:
                logger.warning(f"Batch processing timed out after {timeout}s")
                # Cancel remaining tasks
                for future in future_to_task:
                    future.cancel()
        
        batch_time = time.time() - batch_start
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(
            f"Batch processing completed in {batch_time:.2f}s: "
            f"{successful} successful, {failed} failed"
        )
        
        return results
    
    def process_queue(
        self,
        task_queue: queue.PriorityQueue,
        stop_event: threading.Event
    ):
        """
        Process tasks from a priority queue until stop event is set
        
        Useful for long-running background processing.
        
        Args:
            task_queue: Priority queue of ProcessingTask objects
            stop_event: Event to signal shutdown
        """
        logger.info("Starting queue processor")
        
        while not stop_event.is_set():
            try:
                # Get task with timeout to check stop event periodically
                task = task_queue.get(timeout=1.0)
                
                # Process task
                result = self.process_single(task)
                
                # Mark task as done
                task_queue.task_done()
                
                if not result.success:
                    logger.warning(f"Task failed: {result.session_id} - {result.error}")
            
            except queue.Empty:
                # No tasks available, continue waiting
                continue
            
            except Exception as e:
                logger.error(f"Error in queue processor: {e}", exc_info=True)
        
        logger.info("Queue processor stopped")
    
    def get_statistics(self) -> Dict:
        """
        Get processing statistics
        
        Returns:
            Dictionary with statistics
        """
        with self.stats_lock:
            avg_time = (
                self.stats['total_time'] / self.stats['total_processed']
                if self.stats['total_processed'] > 0
                else 0.0
            )
            
            return {
                'total_processed': self.stats['total_processed'],
                'total_failed': self.stats['total_failed'],
                'total_time': self.stats['total_time'],
                'average_time': avg_time
            }


# Example usage
if __name__ == '__main__':
    from pathlib import Path
    
    # Create test workspace
    workspace = Path('./test_concurrent_workspace')
    workspace.mkdir(exist_ok=True)
    
    # Initialize processor
    processor = ConcurrentObservationalProcessor(
        workspace_dir=workspace,
        max_workers=5
    )
    
    # Create test tasks
    tasks = []
    for i in range(10):
        messages = [
            {
                'role': 'user',
                'content': f'测试消息 {i}',
                'timestamp': datetime.now().isoformat()
            }
        ]
        tasks.append(ProcessingTask(
            session_id=f'session_{i}',
            messages=messages,
            priority=i % 3  # Vary priority
        ))
    
    # Process batch
    results = processor.process_batch(tasks)
    
    # Print results
    print("\n=== Processing Results ===")
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"{status} {result.session_id}: {result.processing_time:.3f}s")
    
    # Print statistics
    stats = processor.get_statistics()
    print("\n=== Statistics ===")
    print(f"Total processed: {stats['total_processed']}")
    print(f"Total failed: {stats['total_failed']}")
    print(f"Average time: {stats['average_time']:.3f}s")
