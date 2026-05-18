"""
database.py
Spairo Academy — Knowledge Evaluator
SQLite storage for all evaluations and reports.
Database file: spairo.db (auto-created on first run)
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "spairo.db"


# ── Schema ────────────────────────────────────────────────────────────────────

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS evaluations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name    TEXT    NOT NULL,
    grade           INTEGER NOT NULL,
    subjects        TEXT    NOT NULL,   -- JSON array: ["Math", "Science"]
    question_count  INTEGER NOT NULL,
    questions       TEXT,               -- JSON array of Question objects
    answers         TEXT,               -- JSON object: {"1": "B", "2": "A"}
    overall_score   INTEGER,
    knowledge_level TEXT,
    subject_scores  TEXT,               -- JSON object: {"Math": 80}
    strengths       TEXT,               -- JSON array
    improvements    TEXT,               -- JSON array
    recommendation  TEXT,
    completed       INTEGER DEFAULT 0,  -- 0 = in progress, 1 = done
    created_at      TEXT    NOT NULL,
    completed_at    TEXT
);
"""


# ── Connection ────────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    return conn


# ── Init ──────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create the database and table if they don't exist. Call once on app start."""
    with _get_conn() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()


# ── Create ────────────────────────────────────────────────────────────────────

def create_evaluation(
    student_name: str,
    grade: int,
    subjects: List[str],
    question_count: int,
    questions: List[Dict]
) -> int:
    """
    Save a new evaluation with generated questions.
    Returns the new evaluation ID.
    """
    sql = """
    INSERT INTO evaluations
        (student_name, grade, subjects, question_count, questions, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    with _get_conn() as conn:
        cursor = conn.execute(sql, (
            student_name.strip().title(),
            grade,
            json.dumps(subjects),
            question_count,
            json.dumps(questions),
            datetime.now().isoformat()
        ))
        conn.commit()
        return cursor.lastrowid


# ── Update: Save Answers ───────────────────────────────────────────────────────

def save_answers(evaluation_id: int, answers: Dict[str, str]) -> None:
    """Store the student's answers (keyed by question id as string)."""
    sql = "UPDATE evaluations SET answers = ? WHERE id = ?"
    with _get_conn() as conn:
        conn.execute(sql, (json.dumps(answers), evaluation_id))
        conn.commit()


# ── Update: Save Report ───────────────────────────────────────────────────────

def save_report(
    evaluation_id: int,
    overall_score: int,
    knowledge_level: str,
    subject_scores: Dict[str, int],
    strengths: List[str],
    improvements: List[str],
    recommendation: str
) -> None:
    """Attach the AI-generated report to an evaluation and mark it complete."""
    sql = """
    UPDATE evaluations SET
        overall_score   = ?,
        knowledge_level = ?,
        subject_scores  = ?,
        strengths       = ?,
        improvements    = ?,
        recommendation  = ?,
        completed       = 1,
        completed_at    = ?
    WHERE id = ?
    """
    with _get_conn() as conn:
        conn.execute(sql, (
            overall_score,
            knowledge_level,
            json.dumps(subject_scores),
            json.dumps(strengths),
            json.dumps(improvements),
            recommendation,
            datetime.now().isoformat(),
            evaluation_id
        ))
        conn.commit()


# ── Read: Single Evaluation ───────────────────────────────────────────────────

def get_evaluation(evaluation_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single evaluation by ID. Returns None if not found."""
    sql = "SELECT * FROM evaluations WHERE id = ?"
    with _get_conn() as conn:
        row = conn.execute(sql, (evaluation_id,)).fetchone()
    if row is None:
        return None
    return _deserialize(dict(row))


# ── Read: All Completed Evaluations ──────────────────────────────────────────

def get_all_evaluations(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch all completed evaluations, newest first.
    Used for the dashboard history list.
    """
    sql = """
    SELECT * FROM evaluations
    WHERE completed = 1
    ORDER BY completed_at DESC
    LIMIT ?
    """
    with _get_conn() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return [_deserialize(dict(r)) for r in rows]


# ── Read: By Student Name ─────────────────────────────────────────────────────

def get_evaluations_by_student(student_name: str) -> List[Dict[str, Any]]:
    """
    Fetch all completed evaluations for a specific student.
    Used for progress trend chart.
    """
    sql = """
    SELECT * FROM evaluations
    WHERE completed = 1 AND student_name = ?
    ORDER BY completed_at ASC
    """
    with _get_conn() as conn:
        rows = conn.execute(sql, (student_name.strip().title(),)).fetchall()
    return [_deserialize(dict(r)) for r in rows]


# ── Read: Student Names List ──────────────────────────────────────────────────

def get_student_names() -> List[str]:
    """Return a sorted list of unique student names with completed evaluations."""
    sql = """
    SELECT DISTINCT student_name FROM evaluations
    WHERE completed = 1
    ORDER BY student_name ASC
    """
    with _get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return [r["student_name"] for r in rows]


# ── Read: Evaluation Count ────────────────────────────────────────────────────

def get_evaluation_count() -> int:
    """Total number of completed evaluations. Used on home page stats."""
    sql = "SELECT COUNT(*) as cnt FROM evaluations WHERE completed = 1"
    with _get_conn() as conn:
        row = conn.execute(sql).fetchone()
    return row["cnt"] if row else 0


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_evaluation(evaluation_id: int) -> None:
    """Hard delete an evaluation record."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM evaluations WHERE id = ?", (evaluation_id,))
        conn.commit()


# ── Helper: Deserialize JSON columns ─────────────────────────────────────────

def _deserialize(row: Dict) -> Dict:
    """
    SQLite stores JSON as text. Convert JSON columns back to Python objects.
    Also formats dates for display.
    """
    json_cols = ["subjects", "questions", "answers", "subject_scores", "strengths", "improvements"]
    for col in json_cols:
        if row.get(col):
            try:
                row[col] = json.loads(row[col])
            except (json.JSONDecodeError, TypeError):
                pass  # Leave as-is if parsing fails

    # Format created_at for display
    for date_col in ["created_at", "completed_at"]:
        if row.get(date_col):
            try:
                dt = datetime.fromisoformat(row[date_col])
                row[f"{date_col}_display"] = dt.strftime("%b %d, %Y  %I:%M %p")
            except ValueError:
                row[f"{date_col}_display"] = row[date_col]

    return row
