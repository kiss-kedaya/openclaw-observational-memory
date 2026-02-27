"""
Observational Memory

Mastra-inspired memory system for AI agents.
"""

__version__ = "2.0.0"

from .core import ObservationalMemoryManager, ObservationExtractor
from .concurrent import ConcurrentObservationalProcessor, ProcessingTask
from .vector import VectorSearchManager, SearchResult
from .data_manager import DataManager

__all__ = [
    "ObservationalMemoryManager",
    "ObservationExtractor",
    "ConcurrentObservationalProcessor",
    "ProcessingTask",
    "VectorSearchManager",
    "SearchResult",
    "DataManager",
    "ObservationalMemory",
]


class ObservationalMemory:
    """
    Unified interface for Observational Memory
    
    Example:
        om = ObservationalMemory()
        om.process_session(session_id, messages)
        om.start_web_ui()
    """
    
    def __init__(self, workspace_dir=None):
        from pathlib import Path
        
        self.workspace_dir = workspace_dir or Path.cwd()
        self.manager = ObservationalMemoryManager(self.workspace_dir)
        self.vector_manager = VectorSearchManager(self.workspace_dir)
        self.concurrent_processor = ConcurrentObservationalProcessor(self.workspace_dir)
        self.data_manager = DataManager(self.workspace_dir)
    
    def process_session(self, session_id, messages):
        """Process a session and generate observations"""
        result = self.manager.process_session(session_id, messages)
        
        # Auto-index for vector search
        observations = result["compressed"].split("\n")
        for obs in observations:
            if obs.strip() and not obs.startswith("Date:"):
                self.vector_manager.index_observation(session_id, obs.strip())
        
        return result
    
    def search(self, query, top_k=5, min_similarity=0.3):
        """Semantic search"""
        return self.vector_manager.search(query, top_k=top_k, min_similarity=min_similarity)
    
    def export_session(self, session_id, format="json"):
        """Export a session"""
        if format == "json":
            return self.data_manager.export_session_json(session_id)
        elif format == "csv":
            return self.data_manager.export_session_csv(session_id)
    
    def backup(self, backup_name=None):
        """Create a backup"""
        return self.data_manager.create_backup(backup_name)
    
    def start_web_ui(self, port=8501):
        """Start Web UI"""
        import subprocess
        import sys
        from pathlib import Path
        
        app_path = Path(__file__).parent.parent / "web" / "app.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)])


def auto_process():
    """Auto-process current OpenClaw session"""
    # TODO: Integrate with OpenClaw
    pass
