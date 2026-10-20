import numpy as np
import pandas as pd

from app.ml.evaluation import evaluate_classification, evaluate_regression
from app.ml.problem_id import identify_problem_type
from app.ml.training import train_model


def _classification_df(n=120):
    rng = np.random.default_rng(0)
    x1 = rng.normal(0, 1, n)
    x2 = rng.choice(["a", "b", "c"], n)
    y = np.where(x1 + rng.normal(0, 0.5, n) > 0, "Yes", "No")
    return pd.DataFrame({"x1": x1, "x2": x2, "target": y})


def _regression_df(n=120):
    rng = np.random.default_rng(0)
    x1 = rng.normal(0, 1, n)
    y = 3 * x1 + rng.normal(0, 0.1, n)
    return pd.DataFrame({"x1": x1, "target": y})


def test_problem_identification_classification():
    df = _classification_df()
    result = identify_problem_type(df, "target")
    assert result["problem_type"] == "classification"


def test_problem_identification_regression():
    df = pd.DataFrame({"x": range(100), "y": np.random.default_rng(0).normal(size=100)})
    result = identify_problem_type(df, "y")
    assert result["problem_type"] == "regression"


def test_train_classification_model():
    df = _classification_df()
    result = train_model(df, "target", ["x1", "x2"], "classification", "RandomForest")
    assert "accuracy" in result["metrics"]
    assert 0 <= result["metrics"]["accuracy"] <= 1


def test_train_regression_model():
    df = _regression_df()
    result = train_model(df, "target", ["x1"], "regression", "LinearRegression")
    assert result["metrics"]["r2"] > 0.8


def test_train_clustering_model():
    df = _regression_df()
    result = train_model(df, None, ["x1"], "clustering", "KMeans", n_clusters=2)
    assert result["metrics"]["n_clusters"] == 2


def test_evaluate_classification_metrics():
    y_true = ["Yes", "No", "Yes", "No"]
    y_pred = ["Yes", "No", "No", "No"]
    metrics = evaluate_classification(y_true, y_pred)
    assert 0 <= metrics["accuracy"] <= 1
    assert "confusion_matrix" in metrics


def test_evaluate_regression_metrics():
    y_true = [1.0, 2.0, 3.0]
    y_pred = [1.1, 1.9, 3.2]
    metrics = evaluate_regression(y_true, y_pred)
    assert metrics["mae"] > 0
    assert metrics["r2"] > 0.9
