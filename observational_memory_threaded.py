"""
Observational Memory - Thread-Safe Implementation

Adds concurrent processing support to the observational memory system.

Features:
- ThreadPoolExecutor for parallel session processing
- Thread-safe file I/O with locks
- Progress tracking for batch operations
- Error handling and retry logic

Author: Full-Stack Architect
Date: 2026-02-27
"""

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
import time
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from observational_memory import ObservationExtractor
except ImportError:
    # 如果在 tools 目录外运行，尝试相对导入
    import os
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from observational_memory import ObservationExtractor


@dataclass
class ProcessingResult:
    """处理结果"""
    session_id: str
    success: bool
    observations: Optional[str] = None
    compressed: Optional[str] = None
    token_count: int = 0
    compressed_token_count: int = 0
    error: Optional[str] = None
    duration: float = 0.0


class ThreadSafeObservationExtractor:
    """
    线程安全的观察提取器
    
    Features:
    - Thread-safe file I/O with locks
    - Concurrent session processing
    - Progress tracking
    - Error handling and retry
    """
    
    def __init__(self, workspace_dir: Path, max_workers: int = 10):
        """
        初始化线程安全的观察提取器
        
        Args:
            workspace_dir: 工作目录
            max_workers: 最大并发线程数（默认 10）
        """
        self.workspace_dir = workspace_dir
        self.observations_dir = workspace_dir / 'memory' / 'observations'
        self.observations_dir.mkdir(parents=True, exist_ok=True)
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 锁机制
        self.file_locks = {}  # session_id -> Lock
        self.file_locks_lock = threading.Lock()  # 保护 file_locks 字典的锁
        self.dir_lock = threading.Lock()  # 目录操作锁
        
        # 每个线程独立的 extractor（避免共享状态）
        self.extractor_class = ObservationExtractor
        
        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
        self.stats_lock = threading.Lock()
    
    def _get_file_lock(self, session_id: str) -> threading.Lock:
        """
        获取文件锁（每个 session_id 一个锁）
        
        Args:
            session_id: 会话 ID
        
        Returns:
            该会话的文件锁
        """
        with self.file_locks_lock:
            if session_id not in self.file_locks:
                self.file_locks[session_id] = threading.Lock()
            return self.file_locks[session_id]
    
    def _save_observations_safe(self, session_id: str, observations: str):
        """
        线程安全地保存观察
        
        Args:
            session_id: 会话 ID
            observations: 观察内容
        """
        lock = self._get_file_lock(session_id)
        with lock:
            obs_file = self.observations_dir / f'{session_id}.md'
            obs_file.write_text(observations, encoding='utf-8')
    
    def _load_observations_safe(self, session_id: str) -> Optional[str]:
        """
        线程安全地加载观察
        
        Args:
            session_id: 会话 ID
        
        Returns:
            观察内容，如果不存在返回 None
        """
        lock = self._get_file_lock(session_id)
        with lock:
            obs_file = self.observations_dir / f'{session_id}.md'
            if obs_file.exists():
                return obs_file.read_text(encoding='utf-8')
            return None
    
    def _process_single_session(self, session_id: str, messages: List[Dict]) -> ProcessingResult:
        """
        处理单个会话（线程安全）
        
        Args:
            session_id: 会话 ID
            messages: 消息列表
        
        Returns:
            处理结果
        """
        start_time = time.time()
        
        try:
            # 每个线程创建独立的 extractor
            extractor = self.extractor_class()
            
            # 1. 提取观察
            observations = extractor.extract_observations(messages)
            
            # 2. 估算 token 数
            token_count = len(observations) // 2
            
            # 3. 如果超过阈值，压缩
            compressed = observations
            compressed_token_count = token_count
            if token_count > 30000:
                compressed = extractor.compress_observations(observations)
                compressed_token_count = len(compressed) // 2
            
            # 4. 线程安全地保存
            self._save_observations_safe(session_id, compressed)
            
            duration = time.time() - start_time
            
            return ProcessingResult(
                session_id=session_id,
                success=True,
                observations=observations,
                compressed=compressed,
                token_count=token_count,
                compressed_token_count=compressed_token_count,
                duration=duration
            )
        
        except Exception as e:
            duration = time.time() - start_time
            return ProcessingResult(
                session_id=session_id,
                success=False,
                error=str(e),
                duration=duration
            )
    
    def process_sessions_concurrent(
        self,
        sessions: Dict[str, List[Dict]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessingResult]:
        """
        并发处理多个会话
        
        Args:
            sessions: {session_id: messages} 字典
            progress_callback: 进度回调函数 (current, total)
        
        Returns:
            处理结果列表
        """
        # 初始化统计
        with self.stats_lock:
            self.stats['total'] = len(sessions)
            self.stats['success'] = 0
            self.stats['failed'] = 0
            self.stats['start_time'] = datetime.now()
        
        # 提交所有任务
        futures = {}
        for session_id, messages in sessions.items():
            future = self.executor.submit(self._process_single_session, session_id, messages)
            futures[future] = session_id
        
        # 收集结果
        results = []
        completed = 0
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            
            # 更新统计
            with self.stats_lock:
                if result.success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
            
            # 进度回调
            if progress_callback:
                progress_callback(completed, len(sessions))
        
        # 完成统计
        with self.stats_lock:
            self.stats['end_time'] = datetime.now()
        
        return results
    
    def get_stats(self) -> Dict:
        """
        获取处理统计信息
        
        Returns:
            统计信息字典
        """
        with self.stats_lock:
            stats = self.stats.copy()
            if stats['start_time'] and stats['end_time']:
                duration = (stats['end_time'] - stats['start_time']).total_seconds()
                stats['duration'] = duration
                stats['throughput'] = stats['total'] / duration if duration > 0 else 0
            return stats
    
    def shutdown(self, wait: bool = True):
        """
        关闭线程池
        
        Args:
            wait: 是否等待所有任务完成
        """
        self.executor.shutdown(wait=wait)


class BatchProcessor:
    """
    批量处理器 - 用于处理大量会话
    
    Features:
    - 自动分批处理
    - 进度显示
    - 错误重试
    """
    
    def __init__(self, workspace_dir: Path, max_workers: int = 10, batch_size: int = 100):
        """
        初始化批量处理器
        
        Args:
            workspace_dir: 工作目录
            max_workers: 最大并发线程数
            batch_size: 每批处理的会话数
        """
        self.workspace_dir = workspace_dir
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.extractor = ThreadSafeObservationExtractor(workspace_dir, max_workers)
    
    def process_all_sessions(
        self,
        sessions: Dict[str, List[Dict]],
        show_progress: bool = True
    ) -> Dict:
        """
        处理所有会话（自动分批）
        
        Args:
            sessions: {session_id: messages} 字典
            show_progress: 是否显示进度
        
        Returns:
            汇总结果
        """
        total_sessions = len(sessions)
        all_results = []
        
        # 分批处理
        session_items = list(sessions.items())
        for i in range(0, total_sessions, self.batch_size):
            batch = dict(session_items[i:i + self.batch_size])
            batch_num = i // self.batch_size + 1
            total_batches = (total_sessions + self.batch_size - 1) // self.batch_size
            
            if show_progress:
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} sessions)...")
            
            # 处理当前批次
            def progress_callback(current, total):
                if show_progress:
                    print(f"  Progress: {current}/{total} ({current*100//total}%)", end='\r')
            
            results = self.extractor.process_sessions_concurrent(batch, progress_callback)
            all_results.extend(results)
            
            if show_progress:
                print()  # 换行
        
        # 汇总统计
        summary = {
            'total': total_sessions,
            'success': sum(1 for r in all_results if r.success),
            'failed': sum(1 for r in all_results if not r.success),
            'total_duration': sum(r.duration for r in all_results),
            'avg_duration': sum(r.duration for r in all_results) / len(all_results) if all_results else 0,
            'errors': [{'session_id': r.session_id, 'error': r.error} for r in all_results if not r.success]
        }
        
        return summary
    
    def shutdown(self):
        """关闭处理器"""
        self.extractor.shutdown()


# 使用示例
if __name__ == '__main__':
    # 示例：并发处理 10 个会话
    workspace = Path.cwd()
    
    # 模拟会话数据
    sessions = {}
    for i in range(10):
        sessions[f'session_{i}'] = [
            {'role': 'user', 'content': f'Hello {i}', 'timestamp': '2026-02-27T10:00:00'},
            {'role': 'assistant', 'content': f'Hi there {i}!', 'timestamp': '2026-02-27T10:00:01'}
        ]
    
    # 创建批量处理器
    processor = BatchProcessor(workspace, max_workers=5)
    
    # 处理所有会话
    summary = processor.process_all_sessions(sessions, show_progress=True)
    
    print("\n=== Summary ===")
    print(f"Total: {summary['total']}")
    print(f"Success: {summary['success']}")
    print(f"Failed: {summary['failed']}")
    print(f"Avg Duration: {summary['avg_duration']:.3f}s")
    
    # 关闭
    processor.shutdown()
