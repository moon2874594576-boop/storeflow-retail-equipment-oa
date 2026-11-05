"""Consistent backups; restoring always creates a new database, never overwrites."""
from __future__ import annotations

import os
from contextlib import closing
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def configured_database():
    sys.path.insert(0, str(ROOT / "backend"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.conf import settings
    return settings.DATABASES["default"]


def reserve_new_file(path: Path):
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents overwriting an existing backup or active database.
    with path.open("xb"):
        pass
    return path


def sqlite_copy(source: Path, target: Path):
    source = source.expanduser().resolve(strict=True)
    if source == target.expanduser().resolve():
        raise ValueError("Source and destination must be different")
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as conn:
        if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("Source SQLite integrity check failed")
        destination = reserve_new_file(target)
        try:
            with closing(sqlite3.connect(destination)) as other:
                conn.backup(other)
                if other.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise ValueError("Destination SQLite integrity check failed")
        except Exception:
            # Only the new file reserved by this operation is removed on failure.
            destination.unlink(missing_ok=True)
            raise
    return destination


def pg_environment(config):
    result = os.environ.copy()
    result.update({"PGHOST": str(config.get("HOST") or "localhost"),
                   "PGPORT": str(config.get("PORT") or "5432"),
                   "PGUSER": str(config.get("USER") or "postgres"),
                   "PGPASSWORD": str(config.get("PASSWORD") or ""),
                   "PGDATABASE": str(config["NAME"])})
    if config.get("OPTIONS", {}).get("sslmode"):
        result["PGSSLMODE"] = config["OPTIONS"]["sslmode"]
    return result


def pg_run(tool, args, config):
    executable = shutil.which(tool)
    if not executable:
        raise RuntimeError(f"{tool} not found; use the app container or install PostgreSQL 16 client tools")
    # Credentials stay in the child environment, not shell command text or logs.
    completed = subprocess.run([executable, *args], env=pg_environment(config),
                               capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"{tool} failed: {completed.stderr.strip()}")


def backup(output: Path, config):
    if config["ENGINE"].endswith("sqlite3"):
        return sqlite_copy(Path(config["NAME"]), output)
    if "postgresql" not in config["ENGINE"]:
        raise ValueError("Only SQLite and PostgreSQL are supported")
    destination = reserve_new_file(output)
    try:
        pg_run("pg_dump", ["--format=custom", "--no-owner", "--no-privileges", "--file", str(destination)], config)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return destination


def restore(source: Path, config, target: Path | None = None, database: str | None = None):
    source = source.expanduser().resolve(strict=True)
    if config["ENGINE"].endswith("sqlite3"):
        if not target or database:
            raise ValueError("SQLite restore requires --target NEW_FILE")
        return str(sqlite_copy(source, target))
    if "postgresql" not in config["ENGINE"]:
        raise ValueError("Only SQLite and PostgreSQL are supported")
    if target or not database or not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", database):
        raise ValueError("PostgreSQL restore requires --database NEW_NAME (lowercase letters, digits, underscore)")
    if database == str(config["NAME"]):
        raise ValueError("Refusing to restore over the configured active database")
    import psycopg
    with psycopg.connect(host=config.get("HOST") or "localhost", port=config.get("PORT") or 5432,
                         user=config.get("USER"), password=config.get("PASSWORD"),
                         dbname=config["NAME"], **config.get("OPTIONS", {})) as conn:
        if conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,)).fetchone():
            raise ValueError("Destination database already exists; choose a new name")
    pg_run("createdb", ["--", database], config)
    pg_run("pg_restore", ["--exit-on-error", "--single-transaction", "--no-owner", "--no-privileges",
                          "--dbname", database, str(source)], config)
    return database
