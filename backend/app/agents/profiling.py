"""Data understanding / profiling agent. Pure pandas/numpy — no LLM."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _col_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    return "categorical"


def profile_dataset(df: pd.DataFrame) -> dict:
    n_rows = len(df)
    columns = []
    numeric_cols, categorical_cols = [], []
    target_candidates = []

    for col in df.columns:
        s = df[col]
        ctype = _col_type(s)
        n_missing = int(s.isna().sum())
        n_unique = int(s.nunique(dropna=True))
        info = {
            "name": str(col),
            "dtype": str(s.dtype),
            "inferred_type": ctype,
            "missing_count": n_missing,
            "missing_pct": round(100 * n_missing / n_rows, 2) if n_rows else 0,
            "unique_count": n_unique,
            "high_cardinality": ctype == "categorical" and n_unique > max(50, int(0.5 * n_rows)),
        }
        if ctype == "numeric":
            numeric_cols.append(col)
            desc = s.describe()
            info.update({
                "mean": _safe_float(desc.get("mean")),
                "std": _safe_float(desc.get("std")),
                "min": _safe_float(desc.get("min")),
                "max": _safe_float(desc.get("max")),
                "median": _safe_float(s.median()),
            })
        else:
            categorical_cols.append(col)
            top = s.value_counts(dropna=True).head(5)
            info["top_values"] = {str(k): int(v) for k, v in top.items()}

        # Target candidate heuristic: low-to-moderate cardinality, not an id-like column
        looks_like_id = str(col).lower() in {"id", "index"} or str(col).lower().endswith("_id")
        if not looks_like_id and 1 < n_unique <= max(20, int(0.2 * n_rows)):
            target_candidates.append(col)

        columns.append(info)

    duplicate_rows = int(df.duplicated().sum())

    # Class imbalance check for low-cardinality categorical/int columns
    imbalance = []
    for col in target_candidates:
        vc = df[col].value_counts(normalize=True, dropna=True)
        if len(vc) >= 2:
            ratio = float(vc.iloc[0] / vc.iloc[-1]) if vc.iloc[-1] > 0 else float("inf")
            if ratio >= 3:
                imbalance.append({"column": str(col), "majority_pct": round(float(vc.iloc[0]) * 100, 2), "imbalance_ratio": round(ratio, 2)})

    return {
        "n_rows": n_rows,
        "n_cols": int(df.shape[1]),
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round(100 * duplicate_rows / n_rows, 2) if n_rows else 0,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "columns": columns,
        "target_candidates": target_candidates,
        "class_imbalance": imbalance,
        "total_missing_cells": int(df.isna().sum().sum()),
    }


def _safe_float(v):
    if v is None:
        return None
    try:
        f = float(v)
        return None if (np.isnan(f) or np.isinf(f)) else round(f, 4)
    except (TypeError, ValueError):
        return None
