import datetime
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("data/job_applications.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    date_applied TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Applied',
    job_post_url TEXT,
    source_text TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def _insert(
    company: str,
    role: str,
    date_applied: str,
    status: str = "Applied",
    job_post_url: Optional[str] = None,
    source_text: Optional[str] = None,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO applications (company, role, date_applied, status, job_post_url, source_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (company, role, date_applied, status, job_post_url, source_text),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def create_application(
    company: str,
    role: str,
    status: str = "Applied",
    job_post_url: Optional[str] = None,
    source_text: Optional[str] = None,
) -> int:
    today = datetime.date.today().isoformat()
    return _insert(
        company=company,
        role=role,
        date_applied=today,
        status=status,
        job_post_url=job_post_url,
        source_text=source_text,
    )


def list_applications() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM applications ORDER BY id").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_status(application_id: int, status: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE applications SET status = ? WHERE id = ?", (status, application_id)
        )
        conn.commit()
    finally:
        conn.close()


def application_exists(company: str, role: str, date_applied: str) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT 1 FROM applications
            WHERE lower(trim(company)) = lower(trim(?))
              AND lower(trim(role)) = lower(trim(?))
              AND date_applied = ?
            LIMIT 1
            """,
            (company, role, date_applied),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def insert_imported_row(
    company: str,
    role: str,
    date_applied: str,
    status: str = "Applied",
    job_post_url: Optional[str] = None,
    source_text: Optional[str] = None,
) -> int:
    return _insert(
        company=company,
        role=role,
        date_applied=date_applied,
        status=status,
        job_post_url=job_post_url,
        source_text=source_text,
    )
