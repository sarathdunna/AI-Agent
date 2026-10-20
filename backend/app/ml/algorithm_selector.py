"""Recommends ML algorithms with pros/cons/assumptions per problem type."""
from __future__ import annotations

CLASSIFICATION_ALGOS = {
    "LogisticRegression": {
        "pros": ["Fast", "Interpretable coefficients", "Works well on linearly separable data"],
        "cons": ["Struggles with non-linear boundaries", "Sensitive to feature scaling"],
        "assumptions": ["Roughly linear relationship between features and log-odds of target"],
    },
    "DecisionTree": {
        "pros": ["Interpretable", "No scaling needed", "Handles non-linear relationships"],
        "cons": ["Prone to overfitting", "Unstable to small data changes"],
        "assumptions": ["None strong; non-parametric"],
    },
    "RandomForest": {
        "pros": ["Robust to overfitting vs single tree", "Handles non-linearity well", "Feature importances available"],
        "cons": ["Less interpretable", "Slower to train/predict than a single tree"],
        "assumptions": ["None strong; non-parametric ensemble"],
    },
    "GradientBoosting": {
        "pros": ["Often highest accuracy", "Handles non-linearity and interactions"],
        "cons": ["Slower to train", "More hyperparameters to tune", "Can overfit if not tuned"],
        "assumptions": ["None strong; sequential ensemble of weak learners"],
    },
    "KNN": {
        "pros": ["Simple, no training phase", "Naturally non-linear"],
        "cons": ["Slow prediction on large data", "Sensitive to feature scaling and irrelevant features"],
        "assumptions": ["Similar points (by distance) share the same label"],
    },
}

REGRESSION_ALGOS = {
    "LinearRegression": {
        "pros": ["Fast", "Interpretable coefficients"],
        "cons": ["Assumes linearity", "Sensitive to outliers"],
        "assumptions": ["Linear relationship, homoscedastic residuals, limited multicollinearity"],
    },
    "Ridge": {
        "pros": ["Handles multicollinearity better than plain linear regression", "Reduces overfitting"],
        "cons": ["Still assumes roughly linear relationship"],
        "assumptions": ["Linear relationship; benefits from feature scaling"],
    },
    "Lasso": {
        "pros": ["Performs feature selection via sparsity", "Reduces overfitting"],
        "cons": ["Can be unstable with correlated features"],
        "assumptions": ["Linear relationship; benefits from feature scaling"],
    },
    "DecisionTreeRegressor": {
        "pros": ["Interpretable", "Captures non-linearity"],
        "cons": ["Prone to overfitting"],
        "assumptions": ["None strong; non-parametric"],
    },
    "RandomForestRegressor": {
        "pros": ["Robust, handles non-linearity", "Feature importances available"],
        "cons": ["Less interpretable", "Slower"],
        "assumptions": ["None strong; non-parametric ensemble"],
    },
    "GradientBoostingRegressor": {
        "pros": ["Often highest accuracy"],
        "cons": ["Slower to train", "More hyperparameters"],
        "assumptions": ["None strong; sequential ensemble"],
    },
}

CLUSTERING_ALGOS = {
    "KMeans": {
        "pros": ["Simple, fast, scalable"],
        "cons": ["Requires choosing k upfront", "Assumes spherical, similarly-sized clusters"],
        "assumptions": ["Clusters are roughly convex/isotropic; features should be scaled"],
    },
}


def recommend_algorithms(problem_type: str) -> dict:
    mapping = {"classification": CLASSIFICATION_ALGOS, "regression": REGRESSION_ALGOS, "clustering": CLUSTERING_ALGOS}
    algos = mapping.get(problem_type, {})
    return {"problem_type": problem_type, "algorithms": [{"name": k, **v} for k, v in algos.items()]}
