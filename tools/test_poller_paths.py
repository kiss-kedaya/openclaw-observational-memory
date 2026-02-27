import sys
sys.path.insert(0, '.')
from session_poller import get_session_files, OPENCLAW_SESSIONS_DIRS

print("Testing Session Poller path configuration...")
print()

print(f"Configured directories: {len(OPENCLAW_SESSIONS_DIRS)}")
for sessions_dir in OPENCLAW_SESSIONS_DIRS:
    print(f"  - {sessions_dir}")
    print(f"    Exists: {sessions_dir.exists()}")
print()

files = get_session_files()
print(f"Total session files found: {len(files)}")

if files:
    print("\nSample files:")
    for f in files[:5]:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")
