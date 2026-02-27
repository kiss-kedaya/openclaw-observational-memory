"""
Observational Memory - Vector Search Extension

Adds semantic search capabilities using vector embeddings.

Features:
- Generate embeddings for observations
- Semantic search with similarity scoring
- Integration with FTS5 for hybrid search
- Support for local embedding models (GGUF)

Author: OpenClaw Community
License: MIT
"""

import sqlite3
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import hashlib
from dataclasses import dataclass

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")


@dataclass
class SearchResult:
    """Result of a semantic search"""
    session_id: str
    observation: str
    similarity: float
    metadata: Optional[Dict] = None


class VectorSearchManager:
    """
    Vector search manager for observational memory
    
    Uses sentence-transformers for generating embeddings and SQLite for storage.
    Supports semantic search with cosine similarity.
    
    Example:
        manager = VectorSearchManager(Path.cwd())
        
        # Index observations
        manager.index_observation('session_1', 'User prefers Python')
        
        # Search
        results = manager.search('programming language preference', top_k=5)
        for result in results:
            print(f'{result.session_id}: {result.observation} (similarity: {result.similarity:.3f})')
    """
    
    def __init__(
        self,
        workspace_dir: Path,
        model_name: str = 'all-MiniLM-L6-v2',
        db_name: str = 'vector_search.db'
    ):
        """
        Initialize vector search manager
        
        Args:
            workspace_dir: Workspace directory
            model_name: Sentence transformer model name
            db_name: SQLite database name
        """
        self.workspace_dir = workspace_dir
        self.db_path = workspace_dir / 'memory' / 'observations' / db_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        else:
            raise RuntimeError("sentence-transformers is required for vector search")
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with vector storage"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create table for embeddings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                observation TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, observation)
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id ON embeddings(session_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def _serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serialize numpy array to bytes"""
        return embedding.astype(np.float32).tobytes()
    
    def _deserialize_embedding(self, data: bytes) -> np.ndarray:
        """Deserialize bytes to numpy array"""
        return np.frombuffer(data, dtype=np.float32)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def index_observation(
        self,
        session_id: str,
        observation: str,
        metadata: Optional[Dict] = None
    ):
        """
        Index an observation with its embedding
        
        Args:
            session_id: Session ID
            observation: Observation text
            metadata: Optional metadata
        """
        # Generate embedding
        embedding = self.generate_embedding(observation)
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO embeddings (session_id, observation, embedding, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                session_id,
                observation,
                self._serialize_embedding(embedding),
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
        finally:
            conn.close()
    
    def index_observations_batch(
        self,
        observations: List[Tuple[str, str, Optional[Dict]]]
    ):
        """
        Index multiple observations in batch
        
        Args:
            observations: List of (session_id, observation, metadata) tuples
        """
        if not observations:
            return
        
        # Generate embeddings in batch
        texts = [obs[1] for obs in observations]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            for (session_id, observation, metadata), embedding in zip(observations, embeddings):
                cursor.execute('''
                    INSERT OR REPLACE INTO embeddings (session_id, observation, embedding, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (
                    session_id,
                    observation,
                    self._serialize_embedding(embedding),
                    json.dumps(metadata) if metadata else None
                ))
            conn.commit()
        finally:
            conn.close()
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0,
        session_filter: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Semantic search for observations
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            session_filter: Optional list of session IDs to filter
        
        Returns:
            List of search results sorted by similarity
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Fetch all embeddings from database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if session_filter:
            placeholders = ','.join('?' * len(session_filter))
            cursor.execute(f'''
                SELECT session_id, observation, embedding, metadata
                FROM embeddings
                WHERE session_id IN ({placeholders})
            ''', session_filter)
        else:
            cursor.execute('''
                SELECT session_id, observation, embedding, metadata
                FROM embeddings
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Calculate similarities
        results = []
        for session_id, observation, embedding_data, metadata_json in rows:
            embedding = self._deserialize_embedding(embedding_data)
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            if similarity >= min_similarity:
                metadata = json.loads(metadata_json) if metadata_json else None
                results.append(SearchResult(
                    session_id=session_id,
                    observation=observation,
                    similarity=similarity,
                    metadata=metadata
                ))
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:top_k]
    
    def delete_session(self, session_id: str):
        """Delete all embeddings for a session"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM embeddings WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM embeddings')
        total_embeddings = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT session_id) FROM embeddings')
        total_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_embeddings': total_embeddings,
            'total_sessions': total_sessions,
            'embedding_dim': self.embedding_dim,
            'model_name': getattr(self.model, '_model_name', 'unknown')
        }


# Integration with ObservationalMemoryManager
def extend_with_vector_search(manager, vector_manager: VectorSearchManager):
    """
    Extend ObservationalMemoryManager with vector search capabilities
    
    Args:
        manager: ObservationalMemoryManager instance
        vector_manager: VectorSearchManager instance
    """
    original_process_session = manager.process_session
    
    def process_session_with_indexing(session_id: str, messages: List[Dict]) -> Dict:
        # Process session normally
        result = original_process_session(session_id, messages)
        
        # Index observations
        observations = result['compressed'].split('\n')
        for obs in observations:
            if obs.strip() and not obs.startswith('Date:'):
                vector_manager.index_observation(session_id, obs.strip())
        
        return result
    
    manager.process_session = process_session_with_indexing
    return manager


# Example usage
if __name__ == '__main__':
    from pathlib import Path
    
    # Initialize
    workspace = Path('./test_vector_workspace')
    workspace.mkdir(exist_ok=True)
    
    manager = VectorSearchManager(workspace)
    
    # Index some observations
    observations = [
        ('session_1', 'User prefers Python for data science', {'priority': 'high'}),
        ('session_1', 'User installed pandas and numpy', {'priority': 'medium'}),
        ('session_2', 'User likes JavaScript for web development', {'priority': 'high'}),
        ('session_2', 'User uses React and Next.js', {'priority': 'medium'}),
    ]
    
    manager.index_observations_batch(observations)
    
    # Search
    print('\n=== Search Results ===')
    results = manager.search('programming language preference', top_k=3)
    for result in results:
        print(f'{result.session_id}: {result.observation}')
        print(f'  Similarity: {result.similarity:.3f}')
        print(f'  Metadata: {result.metadata}')
    
    # Statistics
    print('\n=== Statistics ===')
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f'{key}: {value}')
