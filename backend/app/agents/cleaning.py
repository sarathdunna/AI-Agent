"""Data cleaning agent. Operates on the working dataset copy; original is never mutated."""
from __future__ import annotations

from typing import Any, Literal, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel


class CleaningStep(BaseModel):
    action: Literal[
        "drop_duplicates", "fill_missing", "drop_missing", "drop_column",
        "rename_column", "handle_outliers", "encode_column",
    ]
    columns: Optional[list[str]] = None
    strategy: Optional[str] = None  # mean|median|mode|constant for fill; iqr_clip|iqr_remove for outliers; onehot|label for encode
    value: Optional[Any] = None
    new_name: Optional[str] = None


def apply_cleaning(df: pd.DataFrame, steps: list[CleaningStep]) -> tuple[pd.DataFrame, list[dict]]:
    df = df.copy()
    log: list[dict] = []

    for step in steps:
        before_rows, before_cols = df.shape
        if step.action == "drop_duplicates":
            n_before = len(df)
            df = df.drop_duplicates()
            log.append({"action": step.action, "detail": f"Removed {n_before - len(df)} duplicate rows"})

        elif step.action == "drop_missing":
            cols = step.columns or list(df.columns)
            n_before = len(df)
            df = df.dropna(subset=cols)
            log.append({"action": step.action, "columns": cols, "detail": f"Dropped {n_before - len(df)} rows with missing values"})

        elif step.action == "fill_missing":
            cols = step.columns or df.columns.tolist()
            for col in cols:
                if col not in df.columns:
                    continue
                strategy = step.strategy or "mean"
                if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                    fill = df[col].mean()
                elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                    fill = df[col].median()
                elif strategy == "mode":
                    mode = df[col].mode(dropna=True)
                    fill = mode.iloc[0] if not mode.empty else None
                elif strategy == "constant":
                    fill = step.value
                else:
                    fill = df[col].mean() if pd.api.types.is_numeric_dtype(df[col]) else (df[col].mode().iloc[0] if not df[col].mode().empty else None)
                df[col] = df[col].fillna(fill)
                log.append({"action": step.action, "column": col, "strategy": strategy, "fill_value": str(fill)})

        elif step.action == "drop_column":
            cols = [c for c in (step.columns or []) if c in df.columns]
            df = df.drop(columns=cols)
            log.append({"action": step.action, "columns": cols})

        elif step.action == "rename_column":
            if step.columns and step.new_name:
                df = df.rename(columns={step.columns[0]: step.new_name})
                log.append({"action": step.action, "from": step.columns[0], "to": step.new_name})

        elif step.action == "handle_outliers":
            cols = step.columns or df.select_dtypes(include=[np.number]).columns.tolist()
            for col in cols:
                if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
                    continue
                q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                n_outliers = int(((df[col] < lower) | (df[col] > upper)).sum())
                if step.strategy == "iqr_remove":
                    df = df[(df[col] >= lower) & (df[col] <= upper)]
                else:  # default: clip
                    df[col] = df[col].clip(lower=lower, upper=upper)
                log.append({"action": step.action, "column": col, "strategy": step.strategy or "iqr_clip", "outliers_affected": n_outliers})

        elif step.action == "encode_column":
            cols = step.columns or []
            for col in cols:
                if col not in df.columns:
                    continue
                if step.strategy == "label":
                    df[col] = df[col].astype("category").cat.codes
                    log.append({"action": step.action, "column": col, "strategy": "label"})
                else:
                    dummies = pd.get_dummies(df[col], prefix=col)
                    df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
                    log.append({"action": step.action, "column": col, "strategy": "onehot", "new_columns": list(dummies.columns)})

        log[-1]["shape_before"] = [before_rows, before_cols]
        log[-1]["shape_after"] = list(df.shape)

    return df, log
