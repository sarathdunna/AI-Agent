"""ML problem-type identification based on target dtype/cardinality."""
from __future__ import annotations

import pandas as pd


def identify_problem_type(df: pd.DataFrame, target: str | None) -> dict:
    if target is None or target not in df.columns:
        return {
            "problem_type": "clustering",
            "explanation": "No target column selected, so this is treated as an unsupervised clustering problem.",
        }
    s = df[target].dropna()
    n_unique = s.nunique()
    is_numeric = pd.api.types.is_numeric_dtype(s)

    if is_numeric and n_unique > 20 and (n_unique / max(len(s), 1)) > 0.05:
        return {
            "problem_type": "regression",
            "explanation": (
                f"Target '{target}' is numeric with {n_unique} distinct values (high cardinality relative to "
                f"row count), so this is treated as a regression problem."
            ),
        }
    return {
        "problem_type": "classification",
        "explanation": (
            f"Target '{target}' has {n_unique} distinct value(s)"
            + (" and is non-numeric" if not is_numeric else " and is low-cardinality numeric")
            + ", so this is treated as a classification problem."
        ),
    }
