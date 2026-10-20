"""Visualization agent — produces chart-ready JSON (for Recharts) + AI/template interpretation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.llm_provider import get_llm_provider

SUPPORTED_TYPES = {"bar", "line", "scatter", "histogram", "box", "heatmap", "pie", "count"}


def build_chart(df: pd.DataFrame, chart_type: str, x: str | None = None, y: str | None = None, bins: int = 10) -> dict:
    if chart_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported chart type '{chart_type}'. Supported: {sorted(SUPPORTED_TYPES)}")

    data: list[dict] = []
    meta: dict = {}

    if chart_type in ("bar", "count", "pie"):
        col = x or y
        if col is None or col not in df.columns:
            raise ValueError("A valid column 'x' is required for this chart type")
        vc = df[col].value_counts(dropna=True).head(20)
        data = [{"name": str(k), "value": int(v)} for k, v in vc.items()]

    elif chart_type == "line":
        if x is None or y is None:
            raise ValueError("'x' and 'y' are required for a line chart")
        sub = df[[x, y]].dropna().sort_values(x)
        data = [{"x": _jsonable(r[x]), "y": _jsonable(r[y])} for _, r in sub.iterrows()][:500]

    elif chart_type == "scatter":
        if x is None or y is None:
            raise ValueError("'x' and 'y' are required for a scatter chart")
        sub = df[[x, y]].dropna()
        if len(sub) > 1000:
            sub = sub.sample(1000, random_state=42)
        data = [{"x": _jsonable(r[x]), "y": _jsonable(r[y])} for _, r in sub.iterrows()]

    elif chart_type == "histogram":
        col = x or y
        if col is None:
            raise ValueError("'x' is required for a histogram")
        s = df[col].dropna()
        counts, edges = np.histogram(s, bins=bins)
        data = [{"bin": f"{edges[i]:.2f}-{edges[i+1]:.2f}", "count": int(counts[i])} for i in range(len(counts))]

    elif chart_type == "box":
        col = x or y
        if col is None:
            raise ValueError("'x' is required for a box chart")
        s = df[col].dropna()
        data = [{
            "min": _jsonable(s.min()), "q1": _jsonable(s.quantile(0.25)), "median": _jsonable(s.median()),
            "q3": _jsonable(s.quantile(0.75)), "max": _jsonable(s.max()),
        }]

    elif chart_type == "heatmap":
        numeric = df.select_dtypes(include=[np.number])
        corr = numeric.corr(numeric_only=True).round(4)
        data = [{"x": c1, "y": c2, "value": _jsonable(corr.loc[c1, c2])} for c1 in corr.columns for c2 in corr.columns]
        meta["columns"] = list(corr.columns)

    interpretation = _interpret(chart_type, x, y, data)
    return {"chart_type": chart_type, "x": x, "y": y, "data": data, "meta": meta, "interpretation": interpretation}


def _jsonable(v):
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return round(float(v), 4)
    return v


def _interpret(chart_type: str, x, y, data: list[dict]) -> str:
    llm = get_llm_provider()
    summary = f"Chart type: {chart_type}, x={x}, y={y}, points={len(data)}."
    if llm.is_available():
        return llm.complete(
            system="You are a data visualization assistant. Explain the chart in 2-3 plain-English sentences using ONLY the provided summary data. Do not invent numbers.",
            prompt=f"{summary} Sample data: {data[:10]}",
        )
    # Deterministic template fallback
    if chart_type in ("bar", "count", "pie") and data:
        top = data[0]
        return f"This {chart_type} chart shows {len(data)} categories. The most frequent is '{top['name']}' with {top['value']} occurrences."
    if chart_type == "histogram" and data:
        return f"This histogram groups the values of '{x}' into {len(data)} bins to show the distribution's shape."
    if chart_type == "scatter":
        return f"This scatter plot shows the relationship between '{x}' and '{y}' across {len(data)} points."
    if chart_type == "line":
        return f"This line chart shows how '{y}' changes across '{x}'."
    if chart_type == "box":
        return f"This box plot summarizes the spread and central tendency of '{x}' (min/Q1/median/Q3/max)."
    if chart_type == "heatmap":
        return "This heatmap shows pairwise correlation strength between numeric columns."
    return "Chart generated from the dataset."
