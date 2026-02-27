"""
Install Observational Memory into OpenClaw

Automatically sets up hooks and configuration.
"""

import sys
import shutil
from pathlib import Path
import json


def find_openclaw_dir():
    """Find OpenClaw installation directory"""
    import os
    
    # Try environment variable first
    if "OPENCLAW_HOME" in os.environ:
        path = Path(os.environ["OPENCLAW_HOME"])
        if path.exists():
            return path
    """Find OpenClaw installation directory"""
    # Common locations
    locations = [
        Path(os.path.expanduser("~")) / ".openclaw",
        Path("C:/Users") / Path.home().name / ".openclaw",
        Path("/home") / Path.home().name / ".openclaw",
    ]
    
    for loc in locations:
        if loc.exists() and (loc / "workspace").exists():
            return loc
    
    return None


def install():
    """Install Observational Memory into OpenClaw"""
    print("🔍 Finding OpenClaw installation...")
    
    openclaw_dir = find_openclaw_dir()
    if not openclaw_dir:
        print("❌ OpenClaw not found. Please specify the path:")
        openclaw_dir = Path(input("OpenClaw directory: ").strip())
        
        if not openclaw_dir.exists():
            print("❌ Directory does not exist")
            sys.exit(1)
    
    print(f"✅ Found OpenClaw at: {openclaw_dir}")
    
    # Create hooks directory
    hooks_dir = openclaw_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Copy hook file
    hook_src = Path(__file__).parent / "integrations" / "openclaw_hook.py"
    hook_dst = hooks_dir / "observational_memory_hook.py"
    
    print(f"📦 Installing hook to: {hook_dst}")
    shutil.copy2(hook_src, hook_dst)
    
    # Copy config
    config_src = Path(__file__).parent / "integrations" / "config.json"
    config_dst = hooks_dir / "observational_memory_config.json"
    
    if not config_dst.exists():
        print(f"📝 Creating config: {config_dst}")
        config = json.loads(config_src.read_text())
        config["workspace_dir"] = str(openclaw_dir / "workspace")
        config_dst.write_text(json.dumps(config, indent=2))
    else:
        print(f"⏭️  Config already exists: {config_dst}")
    
    # Install package
    print("📦 Installing observational-memory package...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(Path(__file__).parent)])
    
    print("\n✅ Installation complete!")
    print("\n📖 Next steps:")
    print("1. Restart OpenClaw Gateway")
    print("2. All sessions will be automatically processed")
    print("3. View observations: observational-memory start")
    print("\n🔧 Configuration:")
    print(f"   Edit: {config_dst}")
    print("\n🗑️  Uninstall:")
    print(f"   Delete: {hook_dst}")


if __name__ == "__main__":
    install()
