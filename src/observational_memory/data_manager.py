"""
Data Management Module

Provides import/export and backup functionality for observational memory.

Features:
- Export sessions to JSON/CSV
- Import sessions from JSON
- Backup and restore
- Data migration
"""

import json
import csv
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))

from .core import ObservationalMemoryManager
from .vector import VectorSearchManager


class DataManager:
    """
    Data management for observational memory
    
    Handles import, export, backup, and restore operations.
    """
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.observations_dir = workspace_dir / "memory" / "observations"
        self.backups_dir = workspace_dir / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        self.obs_manager = ObservationalMemoryManager(workspace_dir)
        self.vector_manager = VectorSearchManager(workspace_dir)
    
    def export_session_json(self, session_id: str, output_path: Optional[Path] = None) -> Path:
        """Export a session to JSON"""
        observations = self.obs_manager.load_observations(session_id)
        
        if not observations:
            raise ValueError(f"Session {session_id} not found")
        
        data = {
            "session_id": session_id,
            "observations": observations,
            "exported_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        if output_path is None:
            output_path = self.workspace_dir / f"{session_id}.json"
        
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path
    
    def export_all_json(self, output_dir: Optional[Path] = None) -> List[Path]:
        """Export all sessions to JSON"""
        if output_dir is None:
            output_dir = self.workspace_dir / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        for file in self.observations_dir.glob("*.md"):
            output_path = output_dir / f"{file.stem}.json"
            self.export_session_json(file.stem, output_path)
            exported_files.append(output_path)
        
        return exported_files
    
    def export_session_csv(self, session_id: str, output_path: Optional[Path] = None) -> Path:
        """Export a session to CSV"""
        observations = self.obs_manager.load_observations(session_id)
        
        if not observations:
            raise ValueError(f"Session {session_id} not found")
        
        if output_path is None:
            output_path = self.workspace_dir / f"{session_id}.csv"
        
        lines = observations.split("\n")
        rows = []
        current_date = None
        
        for line in lines:
            if line.startswith("Date:"):
                current_date = line.replace("Date:", "").strip()
            elif line.strip() and line.startswith("*"):
                # Parse observation line
                parts = line.split(")", 1)
                if len(parts) == 2:
                    time_part = parts[0].split("(")[-1].strip()
                    content = parts[1].strip()
                    
                    priority = "Unknown"
                    if "🔴" in line:
                        priority = "High"
                    elif "🟡" in line:
                        priority = "Medium"
                    elif "🟢" in line:
                        priority = "Low"
                    
                    rows.append({
                        "Date": current_date or "",
                        "Time": time_part,
                        "Priority": priority,
                        "Observation": content
                    })
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=["Date", "Time", "Priority", "Observation"])
                writer.writeheader()
                writer.writerows(rows)
        
        return output_path
    
    def import_session_json(self, json_path: Path) -> str:
        """Import a session from JSON"""
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        session_id = data["session_id"]
        observations = data["observations"]
        
        # Save observations
        self.obs_manager.save_observations(session_id, observations)
        
        # Re-index for vector search
        obs_lines = [l.strip() for l in observations.split("\n") if l.strip() and not l.startswith("Date:")]
        for obs in obs_lines:
            self.vector_manager.index_observation(session_id, obs)
        
        return session_id
    
    def create_backup(self, backup_name: Optional[str] = None) -> Path:
        """Create a full backup of all data"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backups_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Backup observations
            if self.observations_dir.exists():
                for file in self.observations_dir.glob("*.md"):
                    zipf.write(file, f"observations/{file.name}")
            
            # Backup vector database
            vector_db = self.workspace_dir / "memory" / "observations" / "vector_search.db"
            if vector_db.exists():
                zipf.write(vector_db, "vector_search.db")
            
            # Add metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_sessions": len(list(self.observations_dir.glob("*.md"))) if self.observations_dir.exists() else 0
            }
            zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        return backup_path
    
    def restore_backup(self, backup_path: Path, overwrite: bool = False):
        """Restore from a backup"""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Create temporary directory
        temp_dir = self.workspace_dir / "temp_restore"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Extract backup
            with zipfile.ZipFile(backup_path, "r") as zipf:
                zipf.extractall(temp_dir)
            
            # Restore observations
            obs_backup_dir = temp_dir / "observations"
            if obs_backup_dir.exists():
                for file in obs_backup_dir.glob("*.md"):
                    target = self.observations_dir / file.name
                    if overwrite or not target.exists():
                        shutil.copy2(file, target)
            
            # Restore vector database
            vector_backup = temp_dir / "vector_search.db"
            if vector_backup.exists():
                vector_target = self.workspace_dir / "memory" / "observations" / "vector_search.db"
                if overwrite or not vector_target.exists():
                    shutil.copy2(vector_backup, vector_target)
        
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        for backup_file in self.backups_dir.glob("*.zip"):
            backups.append({
                "name": backup_file.stem,
                "path": str(backup_file),
                "size": backup_file.stat().st_size,
                "created": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            })
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def delete_backup(self, backup_name: str):
        """Delete a backup"""
        backup_path = self.backups_dir / f"{backup_name}.zip"
        if backup_path.exists():
            backup_path.unlink()
        else:
            raise FileNotFoundError(f"Backup not found: {backup_name}")


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Management for Observational Memory")
    parser.add_argument("action", choices=["export", "import", "backup", "restore", "list-backups"])
    parser.add_argument("--session", help="Session ID")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--output", help="Output path")
    parser.add_argument("--input", help="Input path")
    parser.add_argument("--backup-name", help="Backup name")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    
    args = parser.parse_args()
    
    manager = DataManager(Path.cwd())
    
    if args.action == "export":
        if args.session:
            if args.format == "json":
                path = manager.export_session_json(args.session, Path(args.output) if args.output else None)
            else:
                path = manager.export_session_csv(args.session, Path(args.output) if args.output else None)
            print(f"Exported to: {path}")
        else:
            paths = manager.export_all_json(Path(args.output) if args.output else None)
            print(f"Exported {len(paths)} sessions")
    
    elif args.action == "import":
        if not args.input:
            print("Error: --input required")
            exit(1)
        session_id = manager.import_session_json(Path(args.input))
        print(f"Imported session: {session_id}")
    
    elif args.action == "backup":
        path = manager.create_backup(args.backup_name)
        print(f"Backup created: {path}")
    
    elif args.action == "restore":
        if not args.input:
            print("Error: --input required")
            exit(1)
        manager.restore_backup(Path(args.input), overwrite=args.overwrite)
        print("Backup restored")
    
    elif args.action == "list-backups":
        backups = manager.list_backups()
        print(f"Found {len(backups)} backups:")
        for backup in backups:
            print(f"  - {backup['name']} ({backup['size']} bytes, {backup['created']})")
