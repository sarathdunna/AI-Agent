"""BI dashboard KPI aggregation."""
from __future__ import annotations

import json

import pandas as pd

from app.database import db


def build_dashboard(dataset_id: str, df: pd.DataFrame) -> dict:
    meta = db.get_dataset(dataset_id)
    numeric_count = int(df.select_dtypes(include="number").shape[1])
    categorical_count = int(df.shape[1] - numeric_count)

    models = [m for m in db.list_models() if m["dataset_id"] == dataset_id]
    best_model = None
    if models:
        def score(m):
            metrics = json.loads(m["metrics_json"] or "{}")
            return metrics.get("f1") or metrics.get("r2") or metrics.get("accuracy") or 0
        best_model = max(models, key=score)

    return {
        "dataset_id": dataset_id,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": numeric_count,
        "categorical_columns": categorical_count,
        "is_cleaned": bool(meta["is_cleaned"]) if meta else False,
        "models_trained": len(models),
        "best_model": {
            "id": best_model["id"], "algorithm": best_model["algorithm"], "target": best_model["target"],
            "metrics": json.loads(best_model["metrics_json"] or "{}"),
        } if best_model else None,
    }
