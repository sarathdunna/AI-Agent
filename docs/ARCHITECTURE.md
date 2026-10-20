# Architecture

## High-level diagram

```
┌──────────────────────┐        HTTPS/JSON        ┌───────────────────────────┐
│   React + Vite SPA    │ ────────────────────────▶│      FastAPI backend       │
│  (TypeScript, Tailwind│ ◀────────────────────────│                             │
│   Recharts, Lucide)   │                           │  api/  → routers           │
└──────────────────────┘                           │  agents/ → profiling,      │
                                                     │    cleaning, EDA, viz,     │
                                                     │    query, sql, pandas,     │
                                                     │    insight                 │
                                                     │  ml/ → problem_id,         │
                                                     │    algorithm_selector,     │
                                                     │    preprocessing,          │
                                                     │    training, evaluation,   │
                                                     │    tuning, explainability, │
                                                     │    prediction              │
                                                     │  rag/ → TF-IDF knowledge   │
                                                     │  services/ → dataset I/O,  │
                                                     │    llm_provider, reports   │
                                                     └─────────────┬──────────────┘
                                                                   │
                          ┌────────────────────────────────────────┼─────────────────────┐
                          ▼                                        ▼                      ▼
                 ┌────────────────┐                     ┌────────────────┐     ┌──────────────────┐
                 │ SQLite (app.db) │                     │ uploads/ + CSV  │     │ generated/models  │
                 │ dataset+model   │                     │ working copies  │     │ (.joblib) +       │
                 │ metadata        │                     │ (DuckDB reads   │     │ generated/reports │
                 └────────────────┘                     │  these in-mem)  │     │ (.pdf)            │
                                                          └────────────────┘     └──────────────────┘
                                                                   ▲
                                                                   │ optional
                                                          ┌────────────────┐
                                                          │ Anthropic Claude│
                                                          │ (explanations   │
                                                          │  only — never   │
                                                          │  numeric compute)│
                                                          └────────────────┘
```

## Data flow for a typical session

1. User uploads a CSV/XLSX via `POST /api/datasets/upload`. The file is
   validated (type, size, emptiness, corruption), saved with a UUID-prefixed
   safe filename, converted to a canonical CSV ("original"), and its
   metadata is written to SQLite.
2. `GET /api/datasets/{id}/profile` loads the working copy (original if not
   yet cleaned) into a Pandas DataFrame and runs the profiling agent.
3. `POST /api/datasets/{id}/clean` applies a list of cleaning steps to a
   **copy** of the DataFrame, writes the result as `{id}__working.csv`
   (the original file is never touched), and logs every step.
4. EDA/visualization/query/SQL endpoints all operate on
   `load_working_df()`, so they automatically reflect cleaning.
5. `POST /api/ml/train` builds a `ColumnTransformer` + `Pipeline` fit only on
   the training split, trains the chosen estimator, evaluates on the held-out
   test split, and persists the fitted pipeline with `joblib`. Metadata
   (metrics, feature columns, algorithm) is stored in SQLite; the model file
   path is stored alongside.
6. Predictions load the saved pipeline and apply it to new single-row or
   batch input using the stored feature schema — no retraining needed.

## Why DuckDB for SQL

DuckDB can query a Pandas DataFrame in-memory (`con.register("data", df)`)
without any ETL step, and supports full SQL syntax. Combined with the
allowlist in `app/utils/security.py` (only `SELECT`/`WITH` statements pass;
`DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE/ATTACH/COPY/CREATE/...` are
rejected even if the LLM tries to generate them), this gives safe, fast
ad-hoc analytics.

## Why a separate "original" and "working" dataset

Cleaning is destructive by nature (drop rows/columns, impute, encode). To
support auditability and letting users start over, the original upload is
converted once to an immutable canonical CSV; all cleaning operations write
to a separate `__working.csv`. Every downstream agent reads
`load_working_df()`, which falls back to the original when no cleaning has
occurred yet.
