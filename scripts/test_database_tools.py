"""Independent tests of backup integrity and overwrite prevention."""
from pathlib import Path
from contextlib import closing
import sqlite3
import tempfile
import unittest
from database_tools import backup, restore


class DatabaseToolsTests(unittest.TestCase):
    def test_restore_roundtrip_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "active.sqlite3"
            with closing(sqlite3.connect(source)) as conn:
                conn.execute("CREATE TABLE sample (name TEXT)")
                conn.execute("INSERT INTO sample VALUES (?)", ("门店交接记录",))
                conn.commit()
            config = {"ENGINE": "django.db.backends.sqlite3", "NAME": source}
            archived = backup(root / "archive.sqlite3", config)
            restored = Path(restore(archived, config, root / "restored.sqlite3"))
            with closing(sqlite3.connect(restored)) as conn:
                self.assertEqual(conn.execute("SELECT name FROM sample").fetchone()[0], "门店交接记录")
            with self.assertRaises(FileExistsError):
                backup(archived, config)
            with self.assertRaises(FileExistsError):
                restore(archived, config, source)
            with closing(sqlite3.connect(source)) as conn:
                self.assertEqual(conn.execute("SELECT count(*) FROM sample").fetchone()[0], 1)

    def test_corrupt_archive_does_not_create_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bad = root / "bad.sqlite3"
            bad.write_bytes(b"not a database")
            config = {"ENGINE": "django.db.backends.sqlite3", "NAME": root / "active.sqlite3"}
            with self.assertRaises(sqlite3.DatabaseError):
                restore(bad, config, root / "new.sqlite3")
            self.assertFalse((root / "new.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
