"""
FastAPI backend for Observational Memory
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from observational_memory import ObservationalMemoryManager
from observational_memory_vector import VectorSearchManager
from observational_memory_concurrent import ConcurrentObservationalProcessor

app = FastAPI(
    title="Observational Memory API",
    description="REST API for managing and searching observational memory",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workspace_dir = Path.cwd().parent
obs_manager = ObservationalMemoryManager(workspace_dir)
vector_manager = VectorSearchManager(workspace_dir)

class SessionInfo(BaseModel):
    session_id: str
    observation_count: int
    token_count: int
    last_updated: Optional[str] = None

class Statistics(BaseModel):
    total_sessions: int
    total_observations: int
    total_embeddings: int

@app.get("/")
async def root():
    return {"name": "Observational Memory API", "version": "1.0.0"}

@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions(skip: int = 0, limit: int = 10):
    observations_dir = workspace_dir / "memory" / "observations"
    if not observations_dir.exists():
        return []
    
    session_files = sorted(
        observations_dir.glob("*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )[skip:skip + limit]
    
    sessions = []
    for file in session_files:
        content = file.read_text(encoding="utf-8")
        lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
        sessions.append(SessionInfo(
            session_id=file.stem,
            observation_count=len(lines),
            token_count=len(content) // 2,
            last_updated=datetime.fromtimestamp(file.stat().st_mtime).isoformat()
        ))
    return sessions

@app.get("/statistics", response_model=Statistics)
async def get_statistics():
    observations_dir = workspace_dir / "memory" / "observations"
    total_sessions = len(list(observations_dir.glob("*.md"))) if observations_dir.exists() else 0
    total_observations = 0
    if observations_dir.exists():
        for file in observations_dir.glob("*.md"):
            content = file.read_text(encoding="utf-8")
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
            total_observations += len(lines)
    vector_stats = vector_manager.get_statistics()
    return Statistics(
        total_sessions=total_sessions,
        total_observations=total_observations,
        total_embeddings=vector_stats["total_embeddings"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
