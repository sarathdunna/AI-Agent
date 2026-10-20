"""Model explainability: feature_importances_/coefficients, permutation_importance fallback."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline


def get_feature_names(pipeline: Pipeline) -> list[str]:
    try:
        return list(pipeline.named_steps["pre"].get_feature_names_out())
    except Exception:  # noqa: BLE001
        return []


def explain_model(pipeline: Pipeline, X: pd.DataFrame, y=None) -> dict:
    model = pipeline.named_steps["model"]
    feature_names = get_feature_names(pipeline)
    importances = None
    method = None

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        method = "feature_importances_ (tree-based)"
    elif hasattr(model, "coef_"):
        coef = model.coef_
        importances = np.abs(coef[0]) if coef.ndim > 1 else np.abs(coef)
        method = "absolute coefficients (linear model)"
    elif y is not None:
        try:
            result = permutation_importance(pipeline, X, y, n_repeats=5, random_state=42, n_jobs=-1)
            importances = result.importances_mean
            feature_names = list(X.columns)
            method = "permutation_importance (model-agnostic fallback)"
        except Exception:  # noqa: BLE001
            importances = None

    if importances is None or not feature_names or len(importances) != len(feature_names):
        return {"available": False, "message": "Feature importance could not be computed for this model/data combination.", "features": []}

    order = np.argsort(importances)[::-1]
    ranked = [{"feature": feature_names[i], "importance": round(float(importances[i]), 5)} for i in order]
    top = ranked[0]
    explanation = (
        f"Using {method}, '{top['feature']}' has the largest impact on the model's predictions "
        f"(importance score {top['importance']}). Features are ranked from most to least influential."
    )
    return {"available": True, "method": method, "features": ranked, "explanation": explanation}
