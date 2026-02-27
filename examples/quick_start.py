"""
Quick Start Example for Observational Memory
"""

from observational_memory import ObservationalMemory
from datetime import datetime

# Initialize
om = ObservationalMemory()

# Example messages
messages = [
    {
        "role": "user",
        "content": "帮我安装 agent-browser",
        "timestamp": datetime.now().isoformat()
    },
    {
        "role": "assistant",
        "content": "好的，我来安装",
        "timestamp": datetime.now().isoformat()
    },
    {
        "role": "assistant",
        "content": "安装成功！agent-browser v0.15.0 已就绪",
        "timestamp": datetime.now().isoformat()
    }
]

# Process session
print("Processing session...")
result = om.process_session("example_session", messages)
print(f"Generated {result['token_count']} tokens")
print(f"Observations:\n{result['observations']}")

# Search
print("\nSearching for 'agent-browser'...")
results = om.search("agent-browser", top_k=3)
for i, result in enumerate(results, 1):
    print(f"{i}. {result.session_id}: {result.observation} ({result.similarity:.3f})")

# Export
print("\nExporting session...")
export_path = om.export_session("example_session", format="json")
print(f"Exported to: {export_path}")

# Backup
print("\nCreating backup...")
backup_path = om.backup("example_backup")
print(f"Backup created: {backup_path}")

print("\n✅ Quick start complete!")
print("\nTo start Web UI:")
print("  observational-memory start")
print("\nOr in Python:")
print("  om.start_web_ui()")
