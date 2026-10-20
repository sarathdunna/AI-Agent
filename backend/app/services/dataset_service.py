"""Dataset upload, storage and loading. CSV/XLSX/XLS with validation."""
from __future__ import annotations

import io
import json
import uuid
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import UploadFile

from app.core.config import get_settings
from app.database import db
from app.utils.security import safe_filename, resolve_within

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


class DatasetValidationError(Exception):
    pass


def _read_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
    except Exception as exc:  # noqa: BLE001
        raise DatasetValidationError(f"Could not parse file — it may be corrupt: {exc.__class__.__name__}") from exc
    return df


async def save_upload(file: UploadFile) -> dict:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise DatasetValidationError(f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) == 0:
        raise DatasetValidationError("Uploaded file is empty")
    if len(content) > settings.max_upload_bytes:
        raise DatasetValidationError(f"File exceeds max upload size of {settings.MAX_UPLOAD_MB} MB")

    stored_name = safe_filename(file.filename or "dataset")
    dest = resolve_within(settings.UPLOAD_DIR, stored_name)

    dest.write_bytes(content)

    try:
        df = _read_dataframe(dest)
    except DatasetValidationError:
        dest.unlink(missing_ok=True)
        raise

    if df.shape[0] == 0 or df.shape[1] == 0:
        dest.unlink(missing_ok=True)
        raise DatasetValidationError("Dataset has no rows/columns")

    dataset_id = uuid.uuid4().hex[:12]
    # Also persist a canonical CSV copy (the "original", never mutated) for fast reload.
    original_csv = resolve_within(settings.UPLOAD_DIR, f"{dataset_id}__original.csv")
    df.to_csv(original_csv, index=False)

    row = {
        "id": dataset_id,
        "original_filename": file.filename,
        "stored_filename": original_csv.name,
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns_json": json.dumps(list(df.columns.astype(str))),
        "created_at": db.now_iso(),
        "cleaning_log_json": json.dumps([]),
        "is_cleaned": 0,
    }
    db.insert_dataset(row)
    return row


def get_dataset_meta(dataset_id: str):
    row = db.get_dataset(dataset_id)
    if row is None:
        raise DatasetValidationError("Dataset not found")
    return row


def load_original_df(dataset_id: str) -> pd.DataFrame:
    meta = get_dataset_meta(dataset_id)
    settings = get_settings()
    path = resolve_within(settings.UPLOAD_DIR, meta["stored_filename"])
    return pd.read_csv(path)


def working_path(dataset_id: str) -> Path:
    settings = get_settings()
    return resolve_within(settings.UPLOAD_DIR, f"{dataset_id}__working.csv")


def load_working_df(dataset_id: str) -> pd.DataFrame:
    """Return the cleaned/working dataset if it exists, else the original (never mutated)."""
    wp = working_path(dataset_id)
    if wp.exists():
        return pd.read_csv(wp)
    return load_original_df(dataset_id)


def save_working_df(dataset_id: str, df: pd.DataFrame) -> None:
    df.to_csv(working_path(dataset_id), index=False)
