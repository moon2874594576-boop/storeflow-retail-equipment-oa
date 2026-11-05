"""Print table counts and content digests for comparing a backup/restore or restart."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

from database_tools import configured_database


def summarize(connection, tables):
    result = {}
    for table in sorted(tables):
        # Table names originate from the database catalog and are still quoted.
        quoted = '"' + table.replace('"', '""') + '"'
        with closing(connection.cursor()) as cursor:
            cursor.execute("SELECT * FROM " + quoted)
            rows = sorted(json.dumps(row, ensure_ascii=False, default=str, sort_keys=True) for row in cursor.fetchall())
        digest = hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()
        result[table] = {"count": len(rows), "sha256": digest}
    return result


def snapshot_sqlite(path):
    source = Path(path).expanduser().resolve(strict=True)
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as connection:
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        return summarize(connection, tables)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", type=Path, help="Inspect an explicitly selected SQLite file")
    group.add_argument("--database", help="Inspect another PostgreSQL database using the configured connection")
    args = parser.parse_args()
    if args.file:
        result = snapshot_sqlite(args.file)
    else:
        config = configured_database()
        if config["ENGINE"].endswith("sqlite3"):
            if args.database:
                parser.error("--database is for PostgreSQL; use --file for SQLite")
            result = snapshot_sqlite(config["NAME"])
        else:
            import psycopg
            with psycopg.connect(host=config.get("HOST") or "localhost", port=config.get("PORT") or 5432,
                                 user=config.get("USER"), password=config.get("PASSWORD"),
                                 dbname=args.database or config["NAME"], **config.get("OPTIONS", {})) as connection:
                tables = [row[0] for row in connection.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public'")]
                result = summarize(connection, tables)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
