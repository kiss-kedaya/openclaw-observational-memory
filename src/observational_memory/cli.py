"""
CLI interface for Observational Memory
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Observational Memory CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start Web UI
    start_parser = subparsers.add_parser("start", help="Start Web UI")
    start_parser.add_argument("--port", type=int, default=8501, help="Port number")
    
    # Process session
    process_parser = subparsers.add_parser("process", help="Process a session")
    process_parser.add_argument("session_id", help="Session ID")
    process_parser.add_argument("--messages", help="Messages JSON file")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Semantic search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    
    # Export
    export_parser = subparsers.add_parser("export", help="Export session")
    export_parser.add_argument("session_id", help="Session ID")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")
    
    # Backup
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument("--name", help="Backup name")
    
    args = parser.parse_args()
    
    if args.command == "start":
        from observational_memory import ObservationalMemory
        om = ObservationalMemory()
        om.start_web_ui(port=args.port)
    
    elif args.command == "process":
        from observational_memory import ObservationalMemory
        import json
        
        om = ObservationalMemory()
        
        if args.messages:
            messages = json.loads(Path(args.messages).read_text())
        else:
            print("Error: --messages required")
            sys.exit(1)
        
        result = om.process_session(args.session_id, messages)
        print(f"Processed: {result['token_count']} tokens")
    
    elif args.command == "search":
        from observational_memory import ObservationalMemory
        
        om = ObservationalMemory()
        results = om.search(args.query, top_k=args.top_k)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.session_id} ({result.similarity:.3f})")
            print(f"   {result.observation}")
    
    elif args.command == "export":
        from observational_memory import ObservationalMemory
        
        om = ObservationalMemory()
        path = om.export_session(args.session_id, format=args.format)
        print(f"Exported to: {path}")
    
    elif args.command == "backup":
        from observational_memory import ObservationalMemory
        
        om = ObservationalMemory()
        path = om.backup(backup_name=args.name)
        print(f"Backup created: {path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
