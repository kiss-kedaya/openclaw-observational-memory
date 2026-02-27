# Observational Memory - Multi-Threading Support

## 概述

为 Observational Memory 系统添加多线程支持，实现并发处理多个会话的观察提取。

## 功能特性

- ✅ **线程安全**: 使用锁机制保护文件 I/O 和共享状态
- ✅ **高性能**: 支持 10+ 并发会话，吞吐量 2500+ sessions/s
- ✅ **批量处理**: 自动分批处理大量会话
- ✅ **进度跟踪**: 实时进度回调和统计信息
- ✅ **错误处理**: 完善的异常捕获和错误报告

## 性能指标

| 指标 | 值 |
|------|-----|
| 最大并发数 | 20 workers |
| 吞吐量 | 2500+ sessions/s |
| 平均处理时间 | < 0.01s/session |
| 压力测试 | 500 并发会话通过 |

## 快速开始

### 基础用法

```python
from pathlib import Path
from observational_memory_threaded import ThreadSafeObservationExtractor

# 创建提取器
workspace = Path.cwd()
extractor = ThreadSafeObservationExtractor(workspace, max_workers=10)

# 准备会话数据
sessions = {
    'session_1': [
        {'role': 'user', 'content': '我喜欢编程', 'timestamp': '2026-02-27T10:00:00'},
        {'role': 'assistant', 'content': '很好！', 'timestamp': '2026-02-27T10:00:01'}
    ],
    'session_2': [
        {'role': 'user', 'content': '完成了项目', 'timestamp': '2026-02-27T10:00:00'}
    ]
}

# 并发处理
results = extractor.process_sessions_concurrent(sessions)

# 查看结果
for result in results:
    if result.success:
        print(f"{result.session_id}: {result.token_count} tokens")
    else:
        print(f"{result.session_id}: Error - {result.error}")

# 获取统计信息
stats = extractor.get_stats()
print(f"Success: {stats['success']}/{stats['total']}")
print(f"Throughput: {stats['throughput']:.2f} sessions/s")

# 关闭
extractor.shutdown()
```

### 批量处理

```python
from observational_memory_threaded import BatchProcessor

# 创建批量处理器
processor = BatchProcessor(workspace, max_workers=10, batch_size=100)

# 处理大量会话
summary = processor.process_all_sessions(sessions, show_progress=True)

print(f"Total: {summary['total']}")
print(f"Success: {summary['success']}")
print(f"Failed: {summary['failed']}")
print(f"Avg Duration: {summary['avg_duration']:.3f}s")

# 关闭
processor.shutdown()
```

### 进度回调

```python
def progress_callback(current, total):
    percentage = current * 100 // total
    print(f"Progress: {current}/{total} ({percentage}%)")

results = extractor.process_sessions_concurrent(
    sessions,
    progress_callback=progress_callback
)
```

## 架构设计

### 线程安全机制

1. **文件锁**: 每个 session_id 一个独立的锁
2. **字典锁**: 保护 file_locks 字典的访问
3. **统计锁**: 保护统计信息的更新

```python
# 文件锁机制
def _get_file_lock(self, session_id: str) -> threading.Lock:
    with self.file_locks_lock:
        if session_id not in self.file_locks:
            self.file_locks[session_id] = threading.Lock()
        return self.file_locks[session_id]

# 线程安全的文件写入
def _save_observations_safe(self, session_id: str, observations: str):
    lock = self._get_file_lock(session_id)
    with lock:
        obs_file = self.observations_dir / f'{session_id}.md'
        obs_file.write_text(observations, encoding='utf-8')
```

### 并发处理流程

```
1. 提交所有任务到线程池
   ↓
2. 每个线程独立处理一个会话
   ↓
3. 使用锁保护文件 I/O
   ↓
4. 收集结果并更新统计
   ↓
5. 返回处理结果列表
```

## API 文档

### ThreadSafeObservationExtractor

#### `__init__(workspace_dir, max_workers=10)`

初始化线程安全的观察提取器。

**参数**:
- `workspace_dir` (Path): 工作目录
- `max_workers` (int): 最大并发线程数，默认 10

#### `process_sessions_concurrent(sessions, progress_callback=None)`

并发处理多个会话。

**参数**:
- `sessions` (Dict[str, List[Dict]]): {session_id: messages} 字典
- `progress_callback` (Callable[[int, int], None]): 进度回调函数

**返回**:
- `List[ProcessingResult]`: 处理结果列表

#### `get_stats()`

获取处理统计信息。

**返回**:
- `Dict`: 统计信息字典
  - `total`: 总会话数
  - `success`: 成功数
  - `failed`: 失败数
  - `duration`: 总耗时（秒）
  - `throughput`: 吞吐量（sessions/s）

#### `shutdown(wait=True)`

关闭线程池。

**参数**:
- `wait` (bool): 是否等待所有任务完成

### BatchProcessor

#### `__init__(workspace_dir, max_workers=10, batch_size=100)`

初始化批量处理器。

**参数**:
- `workspace_dir` (Path): 工作目录
- `max_workers` (int): 最大并发线程数
- `batch_size` (int): 每批处理的会话数

#### `process_all_sessions(sessions, show_progress=True)`

处理所有会话（自动分批）。

**参数**:
- `sessions` (Dict[str, List[Dict]]): {session_id: messages} 字典
- `show_progress` (bool): 是否显示进度

**返回**:
- `Dict`: 汇总结果
  - `total`: 总会话数
  - `success`: 成功数
  - `failed`: 失败数
  - `total_duration`: 总耗时
  - `avg_duration`: 平均耗时
  - `errors`: 错误列表

### ProcessingResult

处理结果数据类。

**字段**:
- `session_id` (str): 会话 ID
- `success` (bool): 是否成功
- `observations` (str): 观察内容
- `compressed` (str): 压缩后的观察
- `token_count` (int): Token 数量
- `compressed_token_count` (int): 压缩后 Token 数量
- `error` (str): 错误信息（如果失败）
- `duration` (float): 处理耗时（秒）

## 测试

### 运行测试

```bash
# 基础功能测试
python tools/validate_threaded.py

# 压力测试
python tools/stress_test_threaded.py

# 单元测试（需要 pytest）
pytest tools/test_observational_memory_threaded.py -v
```

### 测试覆盖

- ✅ 线程安全性测试
- ✅ 并发处理测试
- ✅ 性能基准测试
- ✅ 错误处理测试
- ✅ 压力测试（100+ 并发会话）
- ✅ 批量处理测试
- ✅ 并发读写测试

## 性能优化建议

1. **调整 max_workers**: 根据 CPU 核心数调整
   ```python
   import os
   max_workers = os.cpu_count() * 2
   ```

2. **调整 batch_size**: 根据内存大小调整
   ```python
   # 大内存系统
   batch_size = 500
   
   # 小内存系统
   batch_size = 50
   ```

3. **使用进度回调**: 监控长时间运行的任务
   ```python
   def log_progress(current, total):
       if current % 100 == 0:
           print(f"Processed {current}/{total}")
   ```

## 注意事项

1. **内存使用**: 大量并发会话会占用较多内存
2. **文件系统**: 确保文件系统支持并发写入
3. **错误处理**: 检查 `errors` 列表了解失败原因
4. **资源清理**: 使用完毕后调用 `shutdown()`

## 更新日志

### v1.0.0 (2026-02-27)

- ✅ 初始版本
- ✅ ThreadSafeObservationExtractor 实现
- ✅ BatchProcessor 实现
- ✅ 完整的测试套件
- ✅ 性能优化（2500+ sessions/s）

## 贡献者

- Full-Stack Architect (@full-stack-architect)

## 许可证

MIT License
