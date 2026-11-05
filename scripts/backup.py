"""Create a new consistent SQLite or PostgreSQL backup."""
import argparse
import json
from pathlib import Path
from database_tools import backup, configured_database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New backup file; existing files are refused")
    args = parser.parse_args()
    try:
        result = backup(args.output, configured_database())
    except Exception as exc:
        parser.exit(1, f"Backup failed: {exc}\n")
    print(json.dumps({"status": "ok", "backup": str(result)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
