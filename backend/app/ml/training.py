"""ML training service — configures target/features/algorithm/split/seed, trains via sklearn
Pipeline (preprocessing + estimator), saves via joblib."""
from __future__ import annotations

import uuid
from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from app.core.config import get_settings
from app.ml.evaluation import evaluate_classification, evaluate_regression
from app.ml.preprocessing import build_preprocessor

CLASSIFIERS = {
    "LogisticRegression": lambda: LogisticRegression(max_iter=1000),
    "DecisionTree": lambda: DecisionTreeClassifier(random_state=42),
    "RandomForest": lambda: RandomForestClassifier(random_state=42, n_estimators=200),
    "GradientBoosting": lambda: GradientBoostingClassifier(random_state=42),
    "KNN": lambda: KNeighborsClassifier(),
}
REGRESSORS = {
    "LinearRegression": lambda: LinearRegression(),
    "Ridge": lambda: Ridge(),
    "Lasso": lambda: Lasso(),
    "DecisionTreeRegressor": lambda: DecisionTreeRegressor(random_state=42),
    "RandomForestRegressor": lambda: RandomForestRegressor(random_state=42, n_estimators=200),
    "GradientBoostingRegressor": lambda: GradientBoostingRegressor(random_state=42),
}
CLUSTERERS = {
    "KMeans": lambda n_clusters=3: KMeans(random_state=42, n_clusters=n_clusters, n_init=10),
}


def get_estimator(problem_type: str, algorithm: str, **kwargs):
    mapping = {"classification": CLASSIFIERS, "regression": REGRESSORS, "clustering": CLUSTERERS}
    registry = mapping.get(problem_type)
    if registry is None or algorithm not in registry:
        raise ValueError(f"Unknown algorithm '{algorithm}' for problem type '{problem_type}'")
    return registry[algorithm](**kwargs) if kwargs else registry[algorithm]()


def train_model(
    df: pd.DataFrame, target: str | None, feature_columns: list[str], problem_type: str,
    algorithm: str, test_size: float = 0.2, random_state: int = 42, n_clusters: int = 3,
) -> dict:
    settings = get_settings()
    X = df[feature_columns].copy()
    preprocessor = build_preprocessor(df, feature_columns)

    if problem_type == "clustering":
        estimator = get_estimator(problem_type, algorithm, n_clusters=n_clusters)
        pipeline = Pipeline(steps=[("pre", preprocessor), ("model", estimator)])
        labels = pipeline.fit_predict(X)
        metrics = {"n_clusters": n_clusters, "cluster_sizes": pd.Series(labels).value_counts().to_dict()}
        y_test = None
    else:
        y = df[target]
        stratify = y if problem_type == "classification" and y.nunique() > 1 and y.value_counts().min() >= 2 else None
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=stratify)
        estimator = get_estimator(problem_type, algorithm)
        pipeline = Pipeline(steps=[("pre", preprocessor), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        if problem_type == "classification":
            y_proba = None
            if hasattr(pipeline.named_steps["model"], "predict_proba"):
                try:
                    y_proba = pipeline.predict_proba(X_test)
                except Exception:  # noqa: BLE001
                    y_proba = None
            metrics = evaluate_classification(y_test, y_pred, y_proba)
        else:
            metrics = evaluate_regression(y_test, y_pred)

    model_id = uuid.uuid4().hex[:12]
    model_path = settings.MODELS_DIR / f"{model_id}.joblib"
    joblib.dump({
        "pipeline": pipeline,
        "feature_columns": feature_columns,
        "target": target,
        "problem_type": problem_type,
        "algorithm": algorithm,
    }, model_path)

    return {
        "model_id": model_id,
        "model_path": str(model_path),
        "metrics": metrics,
        "problem_type": problem_type,
        "algorithm": algorithm,
        "feature_columns": feature_columns,
        "target": target,
    }


def load_model(model_path: str):
    return joblib.load(model_path)
