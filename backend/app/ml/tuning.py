"""Hyperparameter tuning via RandomizedSearchCV with small, sensible search spaces."""
from __future__ import annotations

import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from app.ml.evaluation import evaluate_classification, evaluate_regression
from app.ml.preprocessing import build_preprocessor
from app.ml.training import get_estimator

SEARCH_SPACES = {
    "RandomForest": {"model__n_estimators": [100, 200, 300], "model__max_depth": [None, 5, 10, 20]},
    "RandomForestRegressor": {"model__n_estimators": [100, 200, 300], "model__max_depth": [None, 5, 10, 20]},
    "GradientBoosting": {"model__n_estimators": [100, 200], "model__learning_rate": [0.01, 0.05, 0.1], "model__max_depth": [2, 3, 4]},
    "GradientBoostingRegressor": {"model__n_estimators": [100, 200], "model__learning_rate": [0.01, 0.05, 0.1], "model__max_depth": [2, 3, 4]},
    "DecisionTree": {"model__max_depth": [None, 3, 5, 10, 20], "model__min_samples_split": [2, 5, 10]},
    "DecisionTreeRegressor": {"model__max_depth": [None, 3, 5, 10, 20], "model__min_samples_split": [2, 5, 10]},
    "KNN": {"model__n_neighbors": [3, 5, 7, 9, 11]},
    "LogisticRegression": {"model__C": [0.01, 0.1, 1, 10]},
    "Ridge": {"model__alpha": [0.1, 1.0, 10.0]},
    "Lasso": {"model__alpha": [0.01, 0.1, 1.0]},
}


def tune_model(df: pd.DataFrame, target: str, feature_columns: list[str], problem_type: str, algorithm: str, test_size: float = 0.2, random_state: int = 42) -> dict:
    X = df[feature_columns]
    y = df[target]
    stratify = y if problem_type == "classification" and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=stratify)

    preprocessor = build_preprocessor(df, feature_columns)
    baseline_estimator = get_estimator(problem_type, algorithm)
    baseline_pipeline = Pipeline(steps=[("pre", preprocessor), ("model", baseline_estimator)])
    baseline_pipeline.fit(X_train, y_train)
    baseline_pred = baseline_pipeline.predict(X_test)
    before_metrics = evaluate_classification(y_test, baseline_pred) if problem_type == "classification" else evaluate_regression(y_test, baseline_pred)

    space = SEARCH_SPACES.get(algorithm)
    if not space:
        return {"tuned": False, "reason": f"No search space defined for '{algorithm}'; baseline metrics returned.", "before": before_metrics, "after": before_metrics, "best_params": {}}

    tuned_estimator = get_estimator(problem_type, algorithm)
    tuned_pipeline = Pipeline(steps=[("pre", preprocessor), ("model", tuned_estimator)])
    scoring = "f1_macro" if problem_type == "classification" else "r2"
    search = RandomizedSearchCV(tuned_pipeline, param_distributions=space, n_iter=8, cv=3, scoring=scoring, random_state=random_state, n_jobs=-1)
    search.fit(X_train, y_train)
    best_pred = search.best_estimator_.predict(X_test)
    after_metrics = evaluate_classification(y_test, best_pred) if problem_type == "classification" else evaluate_regression(y_test, best_pred)

    return {"tuned": True, "before": before_metrics, "after": after_metrics, "best_params": search.best_params_, "best_pipeline": search.best_estimator_}
