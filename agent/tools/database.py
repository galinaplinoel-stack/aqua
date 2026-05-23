"""Database tools - SQLite and PostgreSQL."""

import json
import os
import sqlite3
from typing import Optional

from rich.console import Console

console = Console()


def sqlite_query(db_path: str, query: str, params: Optional[str] = None) -> str:
    """Execute a SQLite query."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        p = json.loads(params) if params else None
        if p:
            cursor.execute(query, p)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith(("SELECT", "PRAGMA")):
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            conn.close()
            return json.dumps(result, indent=2, default=str)
        else:
            conn.commit()
            conn.close()
            return json.dumps({"affected_rows": cursor.rowcount, "lastrowid": cursor.lastrowid})

    except Exception as e:
        return f"SQLite error: {e}"


def sqlite_create_table(db_path: str, table: str, columns: str) -> str:
    """Create a SQLite table."""
    query = f"CREATE TABLE IF NOT EXISTS {table} ({columns})"
    return sqlite_query(db_path, query)


def sqlite_insert(db_path: str, table: str, data: str) -> str:
    """Insert data into SQLite table."""
    try:
        d = json.loads(data)
        columns = ", ".join(d.keys())
        placeholders = ", ".join(["?" for _ in d])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return sqlite_query(db_path, query, json.dumps(list(d.values())))
    except Exception as e:
        return f"Insert error: {e}"


def sqlite_list_tables(db_path: str) -> str:
    """List all tables in SQLite database."""
    return sqlite_query(db_path, "SELECT name FROM sqlite_master WHERE type='table'")


def postgres_query(connection_string: str, query: str, params: Optional[str] = None) -> str:
    """Execute a PostgreSQL query."""
    try:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        p = json.loads(params) if params else None
        if p:
            cursor.execute(query, p)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            conn.close()
            return json.dumps(rows, indent=2, default=str)
        else:
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return json.dumps({"affected_rows": affected})

    except ImportError:
        return "Error: psycopg2 not installed. Run: pip install psycopg2-binary"
    except Exception as e:
        return f"PostgreSQL error: {e}"


DATABASE_TOOLS = {
    "sqlite_query": {
        "func": sqlite_query,
        "schema": {
            "type": "function",
            "function": {
                "name": "sqlite_query",
                "description": "Execute a SQLite query. SELECT queries return results, others return affected rows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_path": {"type": "string", "description": "Path to SQLite database file"},
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "params": {"type": "string", "description": "JSON array of query parameters"},
                    },
                    "required": ["db_path", "query"],
                },
            },
        },
    },
    "sqlite_create_table": {
        "func": sqlite_create_table,
        "schema": {
            "type": "function",
            "function": {
                "name": "sqlite_create_table",
                "description": "Create a SQLite table.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_path": {"type": "string", "description": "Path to SQLite database file"},
                        "table": {"type": "string", "description": "Table name"},
                        "columns": {"type": "string", "description": "Column definitions (e.g., 'id INTEGER PRIMARY KEY, name TEXT')"},
                    },
                    "required": ["db_path", "table", "columns"],
                },
            },
        },
    },
    "sqlite_insert": {
        "func": sqlite_insert,
        "schema": {
            "type": "function",
            "function": {
                "name": "sqlite_insert",
                "description": "Insert a row into a SQLite table.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_path": {"type": "string", "description": "Path to SQLite database file"},
                        "table": {"type": "string", "description": "Table name"},
                        "data": {"type": "string", "description": "JSON object with column:value pairs"},
                    },
                    "required": ["db_path", "table", "data"],
                },
            },
        },
    },
    "postgres_query": {
        "func": postgres_query,
        "schema": {
            "type": "function",
            "function": {
                "name": "postgres_query",
                "description": "Execute a PostgreSQL query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "connection_string": {"type": "string", "description": "PostgreSQL connection string"},
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "params": {"type": "string", "description": "JSON array of query parameters"},
                    },
                    "required": ["connection_string", "query"],
                },
            },
        },
    },
}
