"""
Memory Optimizer

Enhances memory retrieval and management.
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from collections import defaultdict


class MemoryOptimizer:
    """
    Optimizes memory storage and retrieval
    
    Features:
    - Compress similar observations
    - Cluster by topic
    - Export in multiple formats
    - Advanced search
    """
    
    def __init__(self, workspace_dir=None):
        self.workspace_dir = workspace_dir or Path.cwd()
        self.observations_dir = self.workspace_dir / "memory" / "observations"
    
    def compress_observations(self, session_id: str, similarity_threshold=0.8) -> Dict:
        """
        Compress observations by merging similar content
        
        Args:
            session_id: Session identifier
            similarity_threshold: Similarity threshold for merging
            
        Returns:
            Compression statistics
        """
        obs_file = self.observations_dir / f"{session_id}.md"
        if not obs_file.exists():
            return {"error": "Session not found"}
        
        content = obs_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
        
        # Simple deduplication
        unique_lines = []
        seen = set()
        
        for line in lines:
            normalized = line.lower().strip()
            if normalized not in seen:
                unique_lines.append(line)
                seen.add(normalized)
        
        # Write back
        compressed_content = f"Date: {datetime.now().isoformat()}\n\n" + "\n".join(unique_lines)
        obs_file.write_text(compressed_content, encoding="utf-8")
        
        return {
            "original_count": len(lines),
            "compressed_count": len(unique_lines),
            "removed": len(lines) - len(unique_lines),
            "compression_ratio": 1 - (len(unique_lines) / len(lines)) if lines else 0
        }
    
    def cluster_by_topic(self, observations: List[str]) -> Dict[str, List[str]]:
        """
        Cluster observations by topic using keyword extraction
        
        Args:
            observations: List of observations
            
        Returns:
            Dict mapping topics to observations
        """
        clusters = defaultdict(list)
        
        # Simple keyword-based clustering
        keywords = {
            "工具": ["工具", "tool", "安装", "install", "使用", "use"],
            "错误": ["错误", "error", "bug", "问题", "issue"],
            "配置": ["配置", "config", "设置", "setting"],
            "开发": ["开发", "develop", "代码", "code", "编程", "programming"],
            "UI": ["界面", "UI", "页面", "page", "设计", "design"],
            "数据": ["数据", "data", "导出", "export", "备份", "backup"]
        }
        
        for obs in observations:
            matched = False
            for topic, kws in keywords.items():
                if any(kw in obs.lower() for kw in kws):
                    clusters[topic].append(obs)
                    matched = True
                    break
            
            if not matched:
                clusters["其他"].append(obs)
        
        return dict(clusters)
    
    def export_as_markdown(self, session_id: str) -> Path:
        """
        Export session as human-readable Markdown
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to exported file
        """
        obs_file = self.observations_dir / f"{session_id}.md"
        if not obs_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        
        content = obs_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        
        # Format as Markdown
        md_content = f"# 观察记录: {session_id}\n\n"
        md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "## 观察列表\n\n"
        
        for i, line in enumerate(lines, 1):
            if not line.startswith("Date:"):
                md_content += f"{i}. {line}\n"
        
        export_path = self.workspace_dir / "exports" / f"{session_id}_export.md"
        export_path.parent.mkdir(exist_ok=True)
        export_path.write_text(md_content, encoding="utf-8")
        
        return export_path
    
    def export_as_knowledge_graph(self, session_id: str) -> Path:
        """
        Export session as knowledge graph (JSON-LD)
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to exported file
        """
        obs_file = self.observations_dir / f"{session_id}.md"
        if not obs_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        
        content = obs_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
        
        # Build knowledge graph
        graph = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": f"Observations: {session_id}",
            "dateCreated": datetime.now().isoformat(),
            "hasPart": []
        }
        
        for i, line in enumerate(lines, 1):
            graph["hasPart"].append({
                "@type": "CreativeWork",
                "identifier": f"obs_{i}",
                "text": line
            })
        
        export_path = self.workspace_dir / "exports" / f"{session_id}_graph.json"
        export_path.parent.mkdir(exist_ok=True)
        export_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return export_path
    
    def advanced_search(self, query: str, time_range=None, priority=None, regex=False) -> List[Dict]:
        """
        Advanced search with multiple filters
        
        Args:
            query: Search query
            time_range: Tuple of (start, end) datetime
            priority: Priority filter
            regex: Use regex matching
            
        Returns:
            List of matching observations
        """
        results = []
        
        if not self.observations_dir.exists():
            return results
        
        for obs_file in self.observations_dir.glob("*.md"):
            content = obs_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for line in lines:
                if not line.strip() or line.startswith("Date:"):
                    continue
                
                # Query matching
                if regex:
                    import re
                    if not re.search(query, line, re.IGNORECASE):
                        continue
                else:
                    if query.lower() not in line.lower():
                        continue
                
                # Priority filter
                if priority and f"[{priority}]" not in line:
                    continue
                
                results.append({
                    "session_id": obs_file.stem,
                    "observation": line.strip(),
                    "file": str(obs_file)
                })
        
        return results
