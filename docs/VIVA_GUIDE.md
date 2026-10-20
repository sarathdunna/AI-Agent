# Viva Guide — Likely Questions & Simple Answers

## General

**Q: What problem does this project solve?**
A: It lets someone with a spreadsheet but no coding/ML background go from
raw data to a trained, explained machine learning model and a report,
through a guided web UI, without writing code.

**Q: Why FastAPI instead of Flask/Django?**
A: FastAPI gives automatic request validation via Pydantic, automatic
OpenAPI/Swagger docs, and async support, which suits a JSON API backend
that many independent agent modules plug into.

**Q: Why is the LLM optional?**
A: To keep the system usable for free/offline demos and to guarantee that
every numeric result (stats, metrics) comes from real computation
(Pandas/NumPy/scikit-learn), not from an LLM "hallucinating" numbers. The
LLM only writes natural-language explanations and SQL text on top of
already-computed values.

## Data Understanding & Cleaning

**Q: How do you detect a column's type?**
A: Using pandas dtype checks (`is_numeric_dtype`, `is_bool_dtype`,
`is_datetime64_any_dtype`); anything else is treated as categorical.

**Q: How is class imbalance detected?**
A: For candidate target columns, we compute the normalized value counts and
flag it if the ratio between the most and least frequent class is 3x or
more.

**Q: Why keep an "original" and a "working" copy?**
A: So cleaning is reversible/auditable — you can always see what the raw
data looked like, and every cleaning step is logged (before/after shape).

**Q: How are outliers handled?**
A: IQR method: values below Q1-1.5*IQR or above Q3+1.5*IQR are flagged;
they can be clipped to the bounds or removed entirely.

## EDA & Visualization

**Q: What is skewness and why does it matter?**
A: A measure of distribution asymmetry. High skew (|skew| > 1) suggests a
transformation (e.g. log) might help some models, and that mean/std can be
misleading versus median/IQR.

**Q: How does the visualization agent decide what to say about a chart?**
A: It never invents numbers — it either asks the LLM to summarize the exact
data passed to it, or falls back to a deterministic template ("this bar
chart shows N categories, the top one is X with Y occurrences").

## Natural Language / SQL

**Q: How do you prevent SQL injection or destructive SQL from the AI?**
A: `validate_readonly_sql()` only allows queries starting with SELECT/WITH,
rejects multiple statements (no semicolons), and blocklists dangerous
keywords (DROP, DELETE, UPDATE, INSERT, ALTER, ...) as defense-in-depth.
This is tested explicitly in `test_sql_safety.py`.

**Q: What happens if there's no LLM key and a user asks a question?**
A: A rule-based fallback (`_rule_based_sql`) pattern-matches common phrases
("how many rows", "average of column X") into SQL; if nothing matches, it
returns a safe default query (`SELECT * FROM data LIMIT 10`).

## Machine Learning

**Q: How do you decide classification vs regression?**
A: If the target is numeric with high cardinality (>20 distinct values and
>5% of rows distinct) it's regression; otherwise it's classification. No
target selected means clustering.

**Q: How do you avoid data leakage in preprocessing?**
A: The `ColumnTransformer`/`Pipeline` is fit only on the training split
inside `train_test_split`; the same fitted transformers are then applied
(not re-fit) to the test split and to any future prediction input.

**Q: What is the difference between feature_importances_ and permutation
importance?**
A: `feature_importances_` (tree models) is computed during training from
how much each feature reduces impurity. Permutation importance is
model-agnostic: it shuffles one feature at a time on held-out data and
measures the resulting performance drop — used as a fallback when the model
has neither `feature_importances_` nor `coef_`.

**Q: Why RandomizedSearchCV instead of GridSearchCV?**
A: It samples a fixed number of random combinations from the search space
instead of exhaustively trying all of them, which is much faster while
still finding good hyperparameters — appropriate for the small search
budget used here.

**Q: How is ROC-AUC computed for multiclass problems?**
A: Using one-vs-rest (`multi_class="ovr"`) averaging via
`roc_auc_score`.

## Explainability & Reporting

**Q: Why show both pros/cons per algorithm and post-hoc explainability?**
A: Pros/cons help the user pick an algorithm before training (a-priori
guidance); feature importance explains what the trained model actually
learned (a-posteriori). Together they support informed, not black-box,
model use.

**Q: What's in the PDF report?**
A: Dataset overview, a column profile table, deterministic EDA insights,
and (if selected) the chosen model's algorithm, target and metrics —
generated with ReportLab from the same computed data shown in the UI.

## RAG / Knowledge Assistant

**Q: Why TF-IDF instead of a neural embedding model?**
A: It keeps the project lightweight (pure scikit-learn, no GPU/embedding
model download) while still giving reasonable semantic-ish retrieval over a
small, curated 15-document knowledge base — appropriate for an academic
project's scope.

**Q: What happens if no document is relevant to the question?**
A: The similarity threshold (0.08 cosine similarity) filters out weak
matches; if nothing clears it, the API returns an explicit "no relevant
information found" message instead of guessing.
