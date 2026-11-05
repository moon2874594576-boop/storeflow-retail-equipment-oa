"""Restore to a new database; the running application's database is never replaced."""
import argparse
import json
from pathlib import Path
from database_tools import configured_database, restore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", type=Path, help="New SQLite file")
    group.add_argument("--database", help="New PostgreSQL database name")
    args = parser.parse_args()
    try:
        result = restore(args.input, configured_database(), args.target, args.database)
    except Exception as exc:
        parser.exit(1, f"Restore failed: {exc}\n")
    print(json.dumps({"status": "ok", "restored_to": result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
