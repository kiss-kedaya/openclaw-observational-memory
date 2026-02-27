"""
OpenClaw Hook for Observational Memory

Automatically processes all sessions in OpenClaw.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add observational_memory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from observational_memory import ObservationalMemory


class OpenClawHook:
    """
    OpenClaw integration hook
    
    Automatically processes sessions when they reach a threshold.
    """
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.om = ObservationalMemory(workspace_dir=Path(self.config.get("workspace_dir", Path.cwd())))
        self.processed_sessions = set()
    
    def _load_config(self, config_path):
        """Load configuration"""
        if config_path and Path(config_path).exists():
            return json.loads(Path(config_path).read_text())
        
        # Default config
        return {
            "min_messages": 10,
            "auto_index": True,
            "auto_backup": False,
            "backup_interval_hours": 24,
            "workspace_dir": str(Path.cwd())
        }
    
    def should_process(self, session_id, messages):
        """Check if session should be processed"""
        # Already processed recently
        if session_id in self.processed_sessions:
            return False
        
        # Not enough messages
        if len(messages) < self.config["min_messages"]:
            return False
        
        return True
    
    def on_message_complete(self, session_id, messages):
        """
        Hook called after each message
        
        Args:
            session_id: Session identifier
            messages: List of message dicts with role, content, timestamp
        """
        if not self.should_process(session_id, messages):
            return
        
        try:
            # Process session
            result = self.om.process_session(session_id, messages)
            
            # Mark as processed
            self.processed_sessions.add(session_id)
            
            print(f"[ObservationalMemory] Processed {session_id}: {result['token_count']} tokens")
            
            # Auto backup if configured
            if self.config.get("auto_backup"):
                self._maybe_backup()
        
        except Exception as e:
            print(f"[ObservationalMemory] Error processing {session_id}: {e}")
    
    def _maybe_backup(self):
        """Create backup if interval has passed"""
        backup_file = Path(self.om.workspace_dir) / ".last_backup"
        
        if backup_file.exists():
            last_backup = datetime.fromisoformat(backup_file.read_text())
            hours_since = (datetime.now() - last_backup).total_seconds() / 3600
            
            if hours_since < self.config["backup_interval_hours"]:
                return
        
        # Create backup
        try:
            backup_path = self.om.backup()
            backup_file.write_text(datetime.now().isoformat())
            print(f"[ObservationalMemory] Backup created: {backup_path}")
        except Exception as e:
            print(f"[ObservationalMemory] Backup failed: {e}")


# Global hook instance
_hook = None


def initialize(config_path=None):
    """Initialize the hook"""
    global _hook
    _hook = OpenClawHook(config_path)
    return _hook


def on_message_complete(session_id, messages):
    """Hook function called by OpenClaw"""
    if _hook is None:
        initialize()
    _hook.on_message_complete(session_id, messages)


# Auto-initialize
initialize()
