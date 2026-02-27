"""
Tests for Data Management

Run with: pytest test_data_manager.py -v
"""

import pytest
from pathlib import Path
import json
import shutil
from data_manager import DataManager


class TestDataManager:
    """Test data management functionality"""
    
    def setup_method(self):
        self.test_dir = Path("./test_data_manager_workspace")
        self.test_dir.mkdir(exist_ok=True)
        self.manager = DataManager(self.test_dir)
        
        # Create test observations
        obs_dir = self.test_dir / "memory" / "observations"
        obs_dir.mkdir(parents=True, exist_ok=True)
        
        test_obs = """Date: 2026-02-27
* 🔴 (09:00) User stated: Test observation 1
* 🟡 (09:01) Agent completed: Test task"""
        
        (obs_dir / "test_session.md").write_text(test_obs, encoding="utf-8")
    
    def teardown_method(self):
        """Clean up test files"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_export_session_json(self):
        """Test exporting session to JSON"""
        output_path = self.manager.export_session_json("test_session")
        
        assert output_path.exists()
        data = json.loads(output_path.read_text(encoding="utf-8"))
        
        assert data["session_id"] == "test_session"
        assert "observations" in data
        assert "exported_at" in data
        assert data["version"] == "1.0"
    
    def test_export_session_csv(self):
        """Test exporting session to CSV"""
        output_path = self.manager.export_session_csv("test_session")
        
        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        
        assert "Date,Time,Priority,Observation" in content
        assert "High" in content or "Medium" in content
    
    def test_export_all_json(self):
        """Test exporting all sessions"""
        paths = self.manager.export_all_json()
        
        assert len(paths) >= 1
        assert all(p.exists() for p in paths)
    
    def test_import_session_json(self):
        """Test importing session from JSON"""
        # Export first
        export_path = self.manager.export_session_json("test_session")
        
        # Delete original
        (self.test_dir / "memory" / "observations" / "test_session.md").unlink()
        
        # Import
        session_id = self.manager.import_session_json(export_path)
        
        assert session_id == "test_session"
        assert (self.test_dir / "memory" / "observations" / "test_session.md").exists()
    
    def test_create_backup(self):
        """Test creating backup"""
        backup_path = self.manager.create_backup("test_backup")
        
        assert backup_path.exists()
        assert backup_path.suffix == ".zip"
    
    def test_restore_backup(self):
        """Test restoring from backup"""
        # Create backup
        backup_path = self.manager.create_backup("test_backup")
        
        # Delete original
        (self.test_dir / "memory" / "observations" / "test_session.md").unlink()
        
        # Restore
        self.manager.restore_backup(backup_path, overwrite=True)
        
        # Verify
        assert (self.test_dir / "memory" / "observations" / "test_session.md").exists()
    
    def test_list_backups(self):
        """Test listing backups"""
        # Create some backups
        self.manager.create_backup("backup1")
        self.manager.create_backup("backup2")
        
        backups = self.manager.list_backups()
        
        assert len(backups) >= 2
        assert all("name" in b and "path" in b and "size" in b for b in backups)
    
    def test_delete_backup(self):
        """Test deleting backup"""
        backup_path = self.manager.create_backup("test_delete")
        
        self.manager.delete_backup("test_delete")
        
        assert not backup_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
