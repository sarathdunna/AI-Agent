# Project Explanation (M.Tech Report Material)

## Abstract

Organizations and individuals routinely collect tabular data but lack the
combined statistical and machine-learning expertise to turn it into
actionable insight. This project, **Data Analyst + ML Agent**, is a
full-stack web application that automates the standard data-science
workflow — data ingestion, profiling, cleaning, exploratory analysis,
natural-language querying, model selection, training, evaluation,
explainability and reporting — behind a guided, no-code interface. All
numeric computation (statistics, correlations, model metrics) is performed
deterministically with Pandas, NumPy and scikit-learn; a modular Large
Language Model (LLM) integration is used strictly for natural-language
explanation and query translation on top of already-computed values, and the
system remains fully functional without any LLM API key.

## Problem Statement

Non-expert users (analysts, students, small business owners) who possess
tabular data often cannot: (a) systematically assess data quality, (b)
choose an appropriate ML approach for their problem, (c) interpret model
metrics, or (d) query their data without writing code. Existing BI tools
(Power BI, Tableau) handle visualization but not automated ML; existing
AutoML tools (e.g. Google AutoML, H2O) handle ML but offer little
data-understanding or NL-query support, and are often heavyweight, cloud-
locked, or paid.

## Existing System vs Proposed System

| Aspect | Existing tools | Proposed system |
|---|---|---|
| Data profiling | Manual (Excel/Python scripts) | Automated agent with type/missing/imbalance detection |
| Cleaning | Manual scripting | Guided, logged, non-destructive cleaning agent |
| Querying | SQL/Python knowledge required | Natural-language question -> SQL -> answer |
| ML | Requires ML expertise to pick algorithms/tune | Problem-type detection + algorithm recommender + one-click training/tuning |
| Explainability | Often skipped | Built-in feature importance + plain-English metric explanations |
| Cost/lock-in | Many are paid/cloud-only | Open, self-hostable, works with zero external API cost |

## Objectives

1. Provide an end-to-end guided pipeline from raw file upload to a trained,
   explainable ML model and a downloadable report.
2. Keep all numeric results deterministic and auditable (LLM only narrates,
   never computes).
3. Enforce safety for any AI-generated SQL (read-only allowlist).
4. Support classification, regression and clustering with sensible
   algorithm recommendations and metric explanations for non-experts.
5. Ship as a modular, testable, deployable full-stack application.

## System Architecture

See `docs/ARCHITECTURE.md` for a component diagram. In summary: a React SPA
talks to a FastAPI backend over REST/JSON; the backend stores dataset/model
metadata in SQLite, working data as CSV on disk, and trained models as
joblib pickles; DuckDB executes ad-hoc SQL directly against in-memory
Pandas DataFrames; an optional Anthropic Claude client is invoked only for
natural-language explanation/generation tasks.

## Modules

1. **Dataset Service** — validated upload (type/size/corruption/path
   traversal), original vs working copy separation.
2. **Profiling Agent** — column types, missing values, cardinality, target
   candidates, class imbalance.
3. **Cleaning Agent** — duplicate removal, imputation, outlier handling
   (IQR), encoding, rename/drop, with a full audit log.
4. **EDA Agent** — descriptive stats, skewness, correlation, outliers,
   deterministic insight generation.
5. **Visualization Agent** — 8 chart types as Recharts-ready JSON plus
   AI/template interpretation.
6. **Query Agent / SQL Agent** — NL question routed to DuckDB SQL (LLM or
   rule-based fallback), executed under a strict read-only allowlist.
7. **Pandas Agent** — a fixed catalogue of safe operations (groupby, pivot,
   filter, aggregate, correlate) with visible equivalent Python code (no
   arbitrary code execution).
8. **Insight Agent** — deterministic fact extraction (highs/lows, strong
   correlations, anomalies, imbalance), independent of any LLM wrapper.
9. **ML Problem Identification** — classification vs regression vs
   clustering from target dtype/cardinality.
10. **Algorithm Selector** — curated pros/cons/assumptions per algorithm.
11. **Preprocessing** — sklearn `ColumnTransformer`/`Pipeline`, fit only on
    train data (no leakage).
12. **Training Service** — configurable target/features/algorithm/split;
    persists via `joblib`.
13. **Evaluation** — classification (accuracy/precision/recall/F1/ROC-AUC/
    confusion matrix) and regression (MAE/MSE/RMSE/R2) metrics with
    plain-English explanations.
14. **Tuning** — `RandomizedSearchCV` with small, curated search spaces;
    before/after comparison.
15. **Explainability** — `feature_importances_`, linear coefficients, or
    permutation importance fallback.
16. **Prediction** — dynamic single-row and batch (CSV) prediction using the
    saved model's feature schema.
17. **BI Dashboard** — KPI aggregation per dataset.
18. **RAG Knowledge Agent** — 15 markdown documents on core ML/stats
    concepts, retrieved via TF-IDF + cosine similarity.
19. **Report Generator** — PDF via ReportLab.

## Algorithms Used

Classification: Logistic Regression, Decision Tree, Random Forest, Gradient
Boosting, KNN. Regression: Linear, Ridge, Lasso, Decision Tree, Random
Forest, Gradient Boosting Regressors. Clustering: K-Means.

## Methodology

Agile, module-by-module development: each backend agent/service was built
and unit-tested (see `backend/tests/`) in isolation before wiring into the
FastAPI API layer, then the React frontend was built page-by-page against
the typed API client. SQL-injection-style abuse of the AI SQL generator is
specifically tested (`test_sql_safety.py`).
