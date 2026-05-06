"""
THE SYSTEM — Database Connection & Initialization
═══════════════════════════════════════════════════
Handles SQLite connection pooling, schema bootstrap,
and default user seeding.
"""

import sqlite3
from pathlib import Path
from config.settings import DB_PATH, DEFAULT_HUNTER_NAME


_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection with:
    - Row factory for dict-like access
    - Foreign key enforcement enabled
    - WAL journal for concurrent reads
    """
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database() -> None:
    """
    Create all tables from schema.sql if they don't exist,
    then seed a default user if the table is empty.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Execute full schema
    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    cur.executescript(schema_sql)

    # Seed default hunter if no users exist
    cur.execute("SELECT COUNT(*) FROM user_stats")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute(
            "INSERT INTO user_stats (id, username, job_class) VALUES (1, ?, 'None')",
            (DEFAULT_HUNTER_NAME,),
        )
        conn.commit()

    conn.close()


def reset_database() -> None:
    """Drop and recreate all tables. USE WITH CAUTION — destroys all data."""
    db_file = Path(DB_PATH)
    if db_file.exists():
        db_file.unlink()
    init_database()
