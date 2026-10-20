"""Dynamic single-row and batch prediction using a saved model's feature schema."""
from __future__ import annotations

import pandas as pd


def predict_single(model_bundle: dict, input_row: dict) -> dict:
    pipeline = model_bundle["pipeline"]
    feature_columns = model_bundle["feature_columns"]
    missing = [c for c in feature_columns if c not in input_row]
    if missing:
        raise ValueError(f"Missing required feature(s): {missing}")
    row_df = pd.DataFrame([{c: input_row[c] for c in feature_columns}])
    pred = pipeline.predict(row_df)[0]
    result = {"prediction": _jsonable(pred)}
    if hasattr(pipeline, "predict_proba"):
        try:
            proba = pipeline.predict_proba(row_df)[0]
            classes = getattr(pipeline.named_steps["model"], "classes_", None)
            if classes is not None:
                result["probabilities"] = {str(c): round(float(p), 4) for c, p in zip(classes, proba)}
        except Exception:  # noqa: BLE001
            pass
    return result


def predict_batch(model_bundle: dict, df: pd.DataFrame) -> pd.DataFrame:
    pipeline = model_bundle["pipeline"]
    feature_columns = model_bundle["feature_columns"]
    missing = [c for c in feature_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Uploaded file is missing required column(s): {missing}")
    preds = pipeline.predict(df[feature_columns])
    out = df.copy()
    out["prediction"] = preds
    return out


def _jsonable(v):
    try:
        return v.item()  # numpy scalar -> python
    except AttributeError:
        return v
