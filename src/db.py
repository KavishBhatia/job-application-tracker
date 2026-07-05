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
    source_text TEXT,
    total_rounds INTEGER,
    current_round INTEGER,
    feedback TEXT
);
"""

MIGRATION_COLUMNS = {
    "total_rounds": "INTEGER",
    "current_round": "INTEGER",
    "feedback": "TEXT",
}


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(SCHEMA)
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(applications)")}
        for column, coltype in MIGRATION_COLUMNS.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE applications ADD COLUMN {column} {coltype}")
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
    total_rounds: Optional[int] = None,
    current_round: Optional[int] = None,
    feedback: Optional[str] = None,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO applications (
                company, role, date_applied, status, job_post_url, source_text,
                total_rounds, current_round, feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                role,
                date_applied,
                status,
                job_post_url,
                source_text,
                total_rounds,
                current_round,
                feedback,
            ),
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
    total_rounds: Optional[int] = None,
    current_round: Optional[int] = None,
    feedback: Optional[str] = None,
    date_applied: Optional[str] = None,
) -> int:
    date_applied = date_applied or datetime.date.today().isoformat()
    return _insert(
        company=company,
        role=role,
        date_applied=date_applied,
        status=status,
        job_post_url=job_post_url,
        source_text=source_text,
        total_rounds=total_rounds,
        current_round=current_round,
        feedback=feedback,
    )


def list_applications() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT * FROM applications
            ORDER BY
                CASE status
                    WHEN 'Interviewing' THEN 1
                    WHEN 'Applied' THEN 2
                    WHEN 'Rejected' THEN 3
                    WHEN 'Offer' THEN 4
                    WHEN 'Withdrawn' THEN 5
                    ELSE 6
                END,
                date_applied DESC,
                id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_details(
    application_id: int,
    total_rounds: Optional[int],
    current_round: Optional[int],
    feedback: Optional[str],
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE applications
            SET total_rounds = ?, current_round = ?, feedback = ?
            WHERE id = ?
            """,
            (total_rounds, current_round, feedback, application_id),
        )
        conn.commit()
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
    total_rounds: Optional[int] = None,
    current_round: Optional[int] = None,
    feedback: Optional[str] = None,
) -> int:
    return _insert(
        company=company,
        role=role,
        date_applied=date_applied,
        status=status,
        job_post_url=job_post_url,
        source_text=source_text,
        total_rounds=total_rounds,
        current_round=current_round,
        feedback=feedback,
    )
