# Vector Search Guide

## Overview

The observational_memory_vector module adds semantic search capabilities using vector embeddings.

## Features

- **Semantic search**: Find observations by meaning, not just keywords
- **Vector embeddings**: Uses sentence-transformers for high-quality embeddings
- **SQLite storage**: Efficient storage and retrieval of embeddings
- **Hybrid search**: Complements FTS5 full-text search
- **Batch processing**: Efficient batch indexing for large datasets
- **Metadata support**: Store and retrieve metadata with observations

## Quick Start

### Installation

```bash
pip install sentence-transformers torch numpy
```

### Basic Usage

```python
from observational_memory_vector import VectorSearchManager
from pathlib import Path

# Initialize
manager = VectorSearchManager(
    workspace_dir=Path.cwd(),
    model_name='all-MiniLM-L6-v2'  # Fast and accurate
)

# Index observations
manager.index_observation(
    session_id='session_1',
    observation='User prefers Python for data science',
    metadata={'priority': 'high', 'timestamp': '2026-02-27T10:00:00'}
)

# Search
results = manager.search('programming language preference', top_k=5)
for result in results:
    print(f'{result.session_id}: {result.observation}')
    print(f'  Similarity: {result.similarity:.3f}')
```

### Batch Indexing

For better performance with multiple observations:

```python
observations = [
    ('session_1', 'User prefers Python', {'priority': 'high'}),
    ('session_1', 'User installed pandas', {'priority': 'medium'}),
    ('session_2', 'User likes JavaScript', {'priority': 'high'}),
]

manager.index_observations_batch(observations)
```

### Advanced Search

```python
# Search with similarity threshold
results = manager.search(
    query='programming',
    top_k=10,
    min_similarity=0.5  # Only return results with similarity >= 0.5
)

# Search within specific sessions
results = manager.search(
    query='Python',
    top_k=5,
    session_filter=['session_1', 'session_2']
)
```

## Integration with Observational Memory

```python
from observational_memory import ObservationalMemoryManager
from observational_memory_vector import VectorSearchManager, extend_with_vector_search
from pathlib import Path

# Initialize both managers
obs_manager = ObservationalMemoryManager(Path.cwd())
vector_manager = VectorSearchManager(Path.cwd())

# Extend with vector search
obs_manager = extend_with_vector_search(obs_manager, vector_manager)

# Now process_session automatically indexes observations
result = obs_manager.process_session(session_id, messages)

# Search semantically
results = vector_manager.search('user preferences', top_k=5)
```

## Model Selection

### Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| ll-MiniLM-L6-v2 | 80MB | Fast | Good | General purpose (default) |
| ll-mpnet-base-v2 | 420MB | Medium | Excellent | High quality search |
| paraphrase-multilingual-MiniLM-L12-v2 | 420MB | Medium | Good | Multilingual support |

### Custom Models

```python
# Use a different model
manager = VectorSearchManager(
    workspace_dir=Path.cwd(),
    model_name='all-mpnet-base-v2'  # Higher quality
)
```

## Performance

- **Indexing**: ~100 observations in < 10s (batch mode)
- **Search**: < 1s for 100 embeddings
- **Storage**: ~1KB per embedding (384-dimensional vectors)

### Performance Tips

1. **Use batch indexing**: 10x faster than individual indexing
2. **Set appropriate top_k**: Don't retrieve more results than needed
3. **Use similarity threshold**: Filter out irrelevant results early
4. **Session filtering**: Narrow search scope when possible

## API Reference

### VectorSearchManager

```python
manager = VectorSearchManager(
    workspace_dir: Path,
    model_name: str = 'all-MiniLM-L6-v2',
    db_name: str = 'vector_search.db'
)
```

**Methods:**

- generate_embedding(text: str) -> np.ndarray: Generate embedding for text
- index_observation(session_id, observation, metadata=None): Index single observation
- index_observations_batch(observations): Index multiple observations
- search(query, top_k=5, min_similarity=0.0, session_filter=None) -> List[SearchResult]: Semantic search
- delete_session(session_id): Delete all embeddings for a session
- get_statistics() -> Dict: Get database statistics

### SearchResult

```python
result = SearchResult(
    session_id: str,
    observation: str,
    similarity: float,  # Cosine similarity (0.0 to 1.0)
    metadata: Optional[Dict]
)
```

## Hybrid Search (FTS5 + Vector)

Combine full-text search with semantic search for best results:

```python
# Full-text search (fast, exact matches)
fts_results = fts_search('Python programming')

# Semantic search (slower, meaning-based)
vector_results = vector_manager.search('Python programming', top_k=10)

# Combine and deduplicate
all_results = merge_results(fts_results, vector_results)
```

## Storage

Embeddings are stored in SQLite:

```
workspace/
  memory/
    observations/
      vector_search.db  # SQLite database with embeddings
      session_1.md      # Original observations
      session_2.md
```

## Testing

Run tests with coverage:

```bash
pytest test_vector_search.py --cov=observational_memory_vector --cov-report=term-missing
```

Current test coverage: **75%+**

## Troubleshooting

### Model Download Issues

If model download fails:

```python
# Pre-download model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Memory Issues

For large datasets:

```python
# Use smaller model
manager = VectorSearchManager(
    workspace_dir=Path.cwd(),
    model_name='all-MiniLM-L6-v2'  # Smaller, faster
)

# Process in smaller batches
for batch in chunks(observations, 100):
    manager.index_observations_batch(batch)
```

### Slow Search

```python
# Reduce search scope
results = manager.search(
    query='...',
    top_k=5,  # Reduce from 10
    min_similarity=0.5,  # Filter early
    session_filter=['session_1']  # Narrow scope
)
```

## Best Practices

1. **Index incrementally**: Index new observations as they're created
2. **Use metadata**: Store timestamps, priorities, etc. for filtering
3. **Clean up old sessions**: Delete embeddings for inactive sessions
4. **Monitor statistics**: Track database size and performance
5. **Choose appropriate model**: Balance speed vs. quality for your use case

## Future Enhancements

- [ ] Support for local GGUF models (embeddinggemma-300M)
- [ ] Approximate nearest neighbor search (FAISS/Annoy)
- [ ] Multi-modal embeddings (text + images)
- [ ] Incremental indexing with change detection
- [ ] Distributed vector storage
