import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional


DB_PATH = os.environ.get("JOBS_DB_PATH", os.path.join(
    os.path.dirname(__file__), "jobs.db"))


def _ensure_dirs_exist(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def get_connection() -> sqlite3.Connection:
    _ensure_dirs_exist(DB_PATH)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                svg_text TEXT NOT NULL,
                status TEXT NOT NULL,
                plotter_id TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at);
            """
        )


def job_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "svg_text": row["svg_text"],
        "status": row["status"],
        "plotter_id": row["plotter_id"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_job(svg_text: str) -> int:
    now = iso_now()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO jobs(svg_text, status, plotter_id, notes, created_at, updated_at) VALUES (?, 'queued', NULL, NULL, ?, ?)",
            (svg_text, now, now),
        )
        return int(cur.lastrowid)


def list_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM jobs ORDER BY datetime(created_at) DESC LIMIT ?",
            (limit,),
        )
        return [job_row_to_dict(row) for row in cur.fetchall()]


def reserve_next_job(plotter_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        # Begin immediate transaction to prevent race conditions
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM jobs WHERE status = 'queued' ORDER BY datetime(created_at) ASC LIMIT 1"
        ).fetchone()
        if row is None:
            conn.execute("COMMIT")
            return None
        job_id = int(row["id"])
        now = iso_now()
        updated = conn.execute(
            "UPDATE jobs SET status = 'reserved', plotter_id = ?, updated_at = ? WHERE id = ? AND status = 'queued'",
            (plotter_id, now, job_id),
        )
        if updated.rowcount == 0:
            conn.execute("ROLLBACK")
            return None
        reserved = conn.execute(
            "SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        conn.execute("COMMIT")
        return job_row_to_dict(reserved)


ALLOWED_STATUSES = {"queued", "reserved", "started", "completed", "failed"}


def update_job_status(job_id: int, status: str, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    now = iso_now()
    with get_connection() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, notes = COALESCE(?, notes), updated_at = ? WHERE id = ?",
            (status, notes, now, job_id),
        )
        row = conn.execute("SELECT * FROM jobs WHERE id = ?",
                           (job_id,)).fetchone()
        return job_row_to_dict(row) if row else None
