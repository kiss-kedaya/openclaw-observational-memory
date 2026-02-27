"""
Tests for Vector Search

Run with: pytest test_vector_search.py -v
"""

import pytest
from pathlib import Path
import shutil
from observational_memory_vector import (
    VectorSearchManager,
    SearchResult,
    SENTENCE_TRANSFORMERS_AVAILABLE
)


# Skip all tests if sentence-transformers not available
pytestmark = pytest.mark.skipif(
    not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="sentence-transformers not installed"
)


class TestVectorSearchManager:
    """Test vector search manager"""
    
    def setup_method(self):
        self.test_dir = Path('./test_vector_workspace')
        self.test_dir.mkdir(exist_ok=True)
        self.manager = VectorSearchManager(self.test_dir, model_name='all-MiniLM-L6-v2')
    
    def teardown_method(self):
        """Clean up test files"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test manager initialization"""
        assert self.manager.workspace_dir == self.test_dir
        assert self.manager.db_path.exists()
        assert self.manager.embedding_dim > 0
    
    def test_generate_embedding(self):
        """Test embedding generation"""
        text = 'User prefers Python'
        embedding = self.manager.generate_embedding(text)
        
        assert embedding is not None
        assert len(embedding) == self.manager.embedding_dim
        assert embedding.dtype == 'float32' or embedding.dtype == 'float64'
    
    def test_index_observation(self):
        """Test indexing a single observation"""
        self.manager.index_observation(
            'session_1',
            'User prefers Python',
            {'priority': 'high'}
        )
        
        # Verify it was stored
        stats = self.manager.get_statistics()
        assert stats['total_embeddings'] == 1
        assert stats['total_sessions'] == 1
    
    def test_index_observations_batch(self):
        """Test batch indexing"""
        observations = [
            ('session_1', 'User prefers Python', {'priority': 'high'}),
            ('session_1', 'User installed pandas', {'priority': 'medium'}),
            ('session_2', 'User likes JavaScript', {'priority': 'high'}),
        ]
        
        self.manager.index_observations_batch(observations)
        
        stats = self.manager.get_statistics()
        assert stats['total_embeddings'] == 3
        assert stats['total_sessions'] == 2
    
    def test_search_basic(self):
        """Test basic semantic search"""
        # Index observations
        observations = [
            ('session_1', 'User prefers Python for data science', None),
            ('session_2', 'User likes JavaScript for web development', None),
            ('session_3', 'User enjoys cooking Italian food', None),
        ]
        self.manager.index_observations_batch(observations)
        
        # Search for programming-related content
        results = self.manager.search('programming language', top_k=2)
        
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].similarity > results[1].similarity
        
        # Should find programming-related observations
        assert 'Python' in results[0].observation or 'JavaScript' in results[0].observation
    
    def test_search_with_similarity_threshold(self):
        """Test search with minimum similarity"""
        observations = [
            ('session_1', 'User prefers Python', None),
            ('session_2', 'User likes pizza', None),
        ]
        self.manager.index_observations_batch(observations)
        
        # Search with high threshold
        results = self.manager.search('programming', top_k=10, min_similarity=0.3)
        
        # Should only return relevant results
        assert len(results) >= 1
        assert all(r.similarity >= 0.3 for r in results)
    
    def test_search_with_session_filter(self):
        """Test search with session filtering"""
        observations = [
            ('session_1', 'User prefers Python', None),
            ('session_2', 'User prefers Python', None),
            ('session_3', 'User prefers Python', None),
        ]
        self.manager.index_observations_batch(observations)
        
        # Search only in session_1 and session_2
        results = self.manager.search(
            'Python',
            top_k=10,
            session_filter=['session_1', 'session_2']
        )
        
        assert len(results) == 2
        assert all(r.session_id in ['session_1', 'session_2'] for r in results)
    
    def test_delete_session(self):
        """Test deleting session embeddings"""
        observations = [
            ('session_1', 'Observation 1', None),
            ('session_2', 'Observation 2', None),
        ]
        self.manager.index_observations_batch(observations)
        
        # Delete session_1
        self.manager.delete_session('session_1')
        
        stats = self.manager.get_statistics()
        assert stats['total_embeddings'] == 1
        assert stats['total_sessions'] == 1
    
    def test_duplicate_observations(self):
        """Test handling duplicate observations"""
        # Index same observation twice
        self.manager.index_observation('session_1', 'User prefers Python', None)
        self.manager.index_observation('session_1', 'User prefers Python', None)
        
        stats = self.manager.get_statistics()
        # Should only store once (UNIQUE constraint)
        assert stats['total_embeddings'] == 1
    
    def test_metadata_storage(self):
        """Test metadata storage and retrieval"""
        metadata = {'priority': 'high', 'timestamp': '2026-02-27T10:00:00'}
        self.manager.index_observation('session_1', 'Test observation', metadata)
        
        results = self.manager.search('test', top_k=1)
        assert len(results) == 1
        assert results[0].metadata == metadata
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        import numpy as np
        
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        c = np.array([0.0, 1.0, 0.0])
        
        # Identical vectors
        assert abs(self.manager._cosine_similarity(a, b) - 1.0) < 0.001
        
        # Orthogonal vectors
        assert abs(self.manager._cosine_similarity(a, c) - 0.0) < 0.001
    
    def test_empty_search(self):
        """Test search with no indexed observations"""
        results = self.manager.search('anything', top_k=5)
        assert len(results) == 0
    
    def test_statistics(self):
        """Test statistics reporting"""
        observations = [
            ('session_1', 'Obs 1', None),
            ('session_1', 'Obs 2', None),
            ('session_2', 'Obs 3', None),
        ]
        self.manager.index_observations_batch(observations)
        
        stats = self.manager.get_statistics()
        
        assert stats['total_embeddings'] == 3
        assert stats['total_sessions'] == 2
        assert stats['embedding_dim'] > 0
        assert 'model_name' in stats


class TestPerformance:
    """Performance tests"""
    
    def setup_method(self):
        self.test_dir = Path('./test_performance_workspace')
        self.test_dir.mkdir(exist_ok=True)
        self.manager = VectorSearchManager(self.test_dir)
    
    def teardown_method(self):
        """Clean up test files"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_batch_indexing_performance(self):
        """Test batch indexing performance"""
        import time
        
        # Create 100 observations
        observations = [
            (f'session_{i % 10}', f'Observation {i}', None)
            for i in range(100)
        ]
        
        start = time.time()
        self.manager.index_observations_batch(observations)
        elapsed = time.time() - start
        
        print(f'\nIndexed 100 observations in {elapsed:.3f}s')
        assert elapsed < 10.0  # Should complete in under 10 seconds
    
    def test_search_performance(self):
        """Test search performance"""
        import time
        
        # Index 100 observations
        observations = [
            (f'session_{i % 10}', f'User prefers technology {i}', None)
            for i in range(100)
        ]
        self.manager.index_observations_batch(observations)
        
        # Search
        start = time.time()
        results = self.manager.search('technology preference', top_k=10)
        elapsed = time.time() - start
        
        print(f'\nSearched 100 embeddings in {elapsed:.3f}s')
        assert elapsed < 1.0  # Should complete in under 1 second
        assert len(results) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=observational_memory_vector'])
