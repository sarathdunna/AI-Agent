"""EDA agent — computed statistics + deterministic NL insights (no LLM required)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def run_eda(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    descriptive_stats = {}
    skewness = {}
    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        descriptive_stats[col] = {
            "mean": round(float(s.mean()), 4), "median": round(float(s.median()), 4),
            "std": round(float(s.std()), 4), "min": round(float(s.min()), 4), "max": round(float(s.max()), 4),
            "q1": round(float(s.quantile(0.25)), 4), "q3": round(float(s.quantile(0.75)), 4),
        }
        skew = float(s.skew()) if len(s) > 2 else 0.0
        skewness[col] = round(skew, 4)

    correlations = {}
    strong_correlations = []
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True).round(4)
        correlations = corr.to_dict()
        for i, c1 in enumerate(numeric_cols):
            for c2 in numeric_cols[i + 1:]:
                v = corr.loc[c1, c2]
                if pd.notna(v) and abs(v) >= 0.6:
                    strong_correlations.append({"col1": c1, "col2": c2, "correlation": float(v)})

    categorical_frequencies = {}
    for col in categorical_cols:
        vc = df[col].value_counts(dropna=True).head(10)
        categorical_frequencies[col] = {str(k): int(v) for k, v in vc.items()}

    outliers = {}
    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = int(((s < lower) | (s > upper)).sum())
        if n_out:
            outliers[col] = {"count": n_out, "pct": round(100 * n_out / len(s), 2), "lower_bound": round(float(lower), 4), "upper_bound": round(float(upper), 4)}

    insights = _generate_insights(descriptive_stats, strong_correlations, skewness, outliers, df)

    return {
        "descriptive_stats": descriptive_stats,
        "correlations": correlations,
        "strong_correlations": sorted(strong_correlations, key=lambda x: -abs(x["correlation"])),
        "categorical_frequencies": categorical_frequencies,
        "skewness": skewness,
        "outliers": outliers,
        "insights": insights,
    }


def _generate_insights(stats, strong_corr, skewness, outliers, df) -> list[str]:
    insights = []
    for col, sk in skewness.items():
        if abs(sk) > 1:
            direction = "right" if sk > 0 else "left"
            insights.append(f"'{col}' is highly {direction}-skewed (skewness={sk}).")
    for c in strong_corr[:5]:
        strength = "strong" if abs(c["correlation"]) >= 0.8 else "moderate-to-strong"
        direction = "positive" if c["correlation"] > 0 else "negative"
        insights.append(f"'{c['col1']}' and '{c['col2']}' show a {strength} {direction} correlation ({c['correlation']}).")
    for col, o in outliers.items():
        if o["pct"] > 5:
            insights.append(f"'{col}' has {o['count']} outliers ({o['pct']}% of values) outside the IQR bounds.")
    if not insights:
        insights.append("No strong skew, correlation or outlier patterns detected in this dataset.")
    return insights
