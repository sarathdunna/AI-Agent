"""Deterministic fact-extraction agent, separated from any LLM narrative wrapper."""
from __future__ import annotations

import numpy as np
import pandas as pd


def extract_facts(df: pd.DataFrame) -> list[dict]:
    facts: list[dict] = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        idx_max = s.idxmax()
        idx_min = s.idxmin()
        facts.append({"type": "highest", "column": col, "value": float(s.max()), "row_index": int(idx_max)})
        facts.append({"type": "lowest", "column": col, "value": float(s.min()), "row_index": int(idx_min)})

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True)
        for i, c1 in enumerate(numeric_cols):
            for c2 in numeric_cols[i + 1:]:
                v = corr.loc[c1, c2]
                if pd.notna(v) and abs(v) >= 0.6:
                    facts.append({"type": "strong_correlation", "columns": [c1, c2], "value": round(float(v), 4)})

    for col in numeric_cols:
        s = df[col].dropna()
        if len(s) < 3:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = int(((s < lower) | (s > upper)).sum())
        if n_out > 0:
            facts.append({"type": "anomaly", "column": col, "outlier_count": n_out, "pct": round(100 * n_out / len(s), 2)})

    for col in df.columns:
        if col in numeric_cols:
            continue
        vc = df[col].value_counts(normalize=True, dropna=True)
        if len(vc) >= 2 and vc.iloc[-1] > 0 and (vc.iloc[0] / vc.iloc[-1]) >= 3:
            facts.append({"type": "imbalance", "column": col, "majority_value": str(vc.index[0]), "majority_pct": round(float(vc.iloc[0]) * 100, 2)})

    return facts
