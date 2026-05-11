import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

from app_config import DB_PATH

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def _ensure_parent_directory() -> None:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_parent_directory()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _ensure_migrations_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def _load_applied_versions(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def _run_migration_file(connection: sqlite3.Connection, migration_path: Path) -> None:
    migration_sql = migration_path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in migration_sql.split(";") if statement.strip()]
    for statement in statements:
        connection.execute(statement)
    connection.execute(
        "INSERT INTO schema_migrations (version, filename, applied_at) VALUES (?, ?, ?)",
        (migration_path.stem.split("_", 1)[0], migration_path.name, datetime.utcnow().isoformat(timespec="seconds")),
    )


def initialize_database() -> None:
    _ensure_parent_directory()
    if not MIGRATIONS_DIR.exists():
        MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        _ensure_migrations_table(connection)
        applied_versions = _load_applied_versions(connection)
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for migration_file in migration_files:
            version = migration_file.stem.split("_", 1)[0]
            if version in applied_versions:
                continue
            _run_migration_file(connection, migration_file)
        connection.commit()


@contextmanager
def database_session():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()