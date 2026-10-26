import logging
import os
from sqlalchemy import text
from dbapi.database import engine

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_migration_table(conn):
    is_sqlite = conn.dialect.name == "sqlite"
    if is_sqlite:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) UNIQUE NOT NULL,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    else:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    conn.execute(text(create_table_sql))


def get_applied_migrations(conn):
    result = conn.execute(text("SELECT filename FROM schema_migrations"))
    return {row[0] for row in result.fetchall()}


def run_migrations():
    logger.info("Checking and running pending database migrations...")
    sql_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")])

    with engine.begin() as conn:
        ensure_migration_table(conn)
        applied = get_applied_migrations(conn)

        for filename in sql_files:
            if filename in applied:
                continue

            file_path = os.path.join(MIGRATIONS_DIR, filename)
            logger.info(f"Applying migration: {filename}")
            with open(file_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # Handle dialect compatibility if running against SQLite locally
            if conn.dialect.name == "sqlite":
                sql_content = sql_content.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
                sql_content = sql_content.replace("DOUBLE PRECISION", "REAL")
                sql_content = sql_content.replace("TIMESTAMP WITH TIME ZONE", "DATETIME")
                sql_content = sql_content.replace("TIMESTAMPTZ", "DATETIME")

            # Split statements if necessary and execute
            statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
            for stmt in statements:
                conn.execute(text(stmt))

            conn.execute(
                text("INSERT INTO schema_migrations (filename) VALUES (:filename)"),
                {"filename": filename},
            )
            logger.info(f"Migration {filename} applied successfully.")

    logger.info("All database migrations are up to date.")
