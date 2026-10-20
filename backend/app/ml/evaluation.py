"""Model evaluation metrics + plain-English explanations."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score,
)

METRIC_EXPLANATIONS = {
    "accuracy": "The percentage of predictions the model got exactly right.",
    "precision": "Of everything the model predicted as positive, the fraction that was actually positive.",
    "recall": "Of everything that was actually positive, the fraction the model correctly caught.",
    "f1": "The harmonic mean of precision and recall — a balance between the two.",
    "roc_auc": "The model's ability to rank positive cases higher than negative ones (1.0 = perfect, 0.5 = random).",
    "mae": "Mean Absolute Error — average absolute difference between predicted and actual values (same units as target).",
    "mse": "Mean Squared Error — average of squared differences; penalizes large errors more.",
    "rmse": "Root Mean Squared Error — square root of MSE, back in the original units of the target.",
    "r2": "R-squared — the proportion of variance in the target explained by the model (1.0 = perfect fit).",
}


def evaluate_classification(y_true, y_pred, y_proba=None) -> dict:
    labels = set(y_true)
    # "binary" averaging requires numeric {0,1} labels (pos_label defaults to 1);
    # for string labels (e.g. "Yes"/"No") or multiclass, "weighted" is used instead.
    average = "binary" if labels <= {0, 1} else "weighted"
    metrics = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, average=average, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, average=average, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, average=average, zero_division=0)), 4),
    }
    if y_proba is not None:
        try:
            if y_proba.ndim == 2 and y_proba.shape[1] == 2:
                metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_proba[:, 1])), 4)
            elif y_proba.ndim == 2 and y_proba.shape[1] > 2:
                metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_proba, multi_class="ovr")), 4)
        except Exception:  # noqa: BLE001
            pass
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()
    metrics["explanations"] = {k: METRIC_EXPLANATIONS[k] for k in metrics if k in METRIC_EXPLANATIONS}
    return metrics


def evaluate_regression(y_true, y_pred) -> dict:
    mse = float(mean_squared_error(y_true, y_pred))
    metrics = {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "mse": round(mse, 4),
        "rmse": round(float(np.sqrt(mse)), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }
    metrics["explanations"] = {k: METRIC_EXPLANATIONS[k] for k in metrics if k in METRIC_EXPLANATIONS}
    return metrics
