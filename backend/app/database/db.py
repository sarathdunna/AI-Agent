"""Lightweight SQLite metadata store (datasets, models). No ORM needed for this scope."""
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

from app.core.config import get_settings

_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    settings = get_settings()
    conn = sqlite3.connect(str(settings.DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    with _lock:
        conn = _connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                original_filename TEXT,
                stored_filename TEXT,
                n_rows INTEGER,
                n_cols INTEGER,
                columns_json TEXT,
                created_at TEXT,
                cleaning_log_json TEXT DEFAULT '[]',
                is_cleaned INTEGER DEFAULT 0
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,
                dataset_id TEXT,
                target TEXT,
                problem_type TEXT,
                algorithm TEXT,
                feature_columns_json TEXT,
                metrics_json TEXT,
                params_json TEXT,
                model_path TEXT,
                created_at TEXT
            )"""
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_dataset(row: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO datasets (id, original_filename, stored_filename, n_rows, n_cols, columns_json,
                created_at, cleaning_log_json, is_cleaned)
               VALUES (:id, :original_filename, :stored_filename, :n_rows, :n_cols, :columns_json,
                :created_at, :cleaning_log_json, :is_cleaned)""",
            row,
        )


def get_dataset(dataset_id: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        return cur.fetchone()


def list_datasets() -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM datasets ORDER BY created_at DESC")
        return cur.fetchall()


def update_dataset_cleaning(dataset_id: str, cleaning_log: list, n_rows: int, n_cols: int, columns: list) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE datasets SET cleaning_log_json = ?, is_cleaned = 1, n_rows = ?, n_cols = ?, columns_json = ? WHERE id = ?",
            (json.dumps(cleaning_log), n_rows, n_cols, json.dumps(columns), dataset_id),
        )


def insert_model(row: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO models (id, dataset_id, target, problem_type, algorithm, feature_columns_json,
                metrics_json, params_json, model_path, created_at)
               VALUES (:id, :dataset_id, :target, :problem_type, :algorithm, :feature_columns_json,
                :metrics_json, :params_json, :model_path, :created_at)""",
            row,
        )


def get_model(model_id: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        return cur.fetchone()


def list_models() -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM models ORDER BY created_at DESC")
        return cur.fetchall()


def update_model_metrics(model_id: str, metrics: dict, params: dict) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE models SET metrics_json = ?, params_json = ? WHERE id = ?",
            (json.dumps(metrics), json.dumps(params), model_id),
        )
