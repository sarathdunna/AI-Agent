# Demo Guide (15-step script)

1. Start the backend (`uvicorn app.main:app --reload`) and frontend
   (`npm run dev`); open http://localhost:5173.
2. On the **Dashboard**, point out the hero section and workflow diagram.
3. Click **Upload Dataset**, select `sample_data/customer_churn_sample.csv`.
4. You land on **Data Profile** — show row/column counts, missing %, target
   candidates, and the class-imbalance callout for `churn`.
5. Go to **Data Cleaning** — add a "Drop duplicates" step and a "Fill
   missing (mean)" step, click Apply, show the cleaning log.
6. Go to **EDA** — show descriptive stats, the strong-correlation list
   (tenure vs total_charges), and the deterministic insight bullets.
7. Go to **Visualizations** — generate a bar chart of `contract_type`, then
   a histogram of `monthly_charges`; read the interpretation text aloud.
8. Go to **Ask Data** — click the example prompt "How many rows are in this
   dataset?", show the SQL it generated and the explanation.
9. Go to **SQL Agent** — type "average monthly charges by contract type",
   generate SQL, run it; then try editing the SQL to `DROP TABLE data` and
   show it gets rejected with a clear safety message.
10. Go to **ML Studio** — Step 1: select target `churn`. Step 2: problem type
    auto-detected as classification, with an explanation. Step 3: select
    feature columns. Step 4: pick Random Forest, show pros/cons.
11. Step 5: set test split to 20%, enable hyperparameter tuning. Step 6:
    click Train.
12. Show the resulting metrics (accuracy, precision, recall, F1, ROC-AUC,
    confusion matrix) and the before/after tuning comparison.
13. Scroll to **Explainability** — show the feature importance bar list and
    its plain-English explanation.
14. Go to **Predictions** — fill in a single row manually and predict churn
    probability; then upload a small CSV for batch prediction.
15. Go to **Reports**, generate and download the PDF report; briefly open it
    to show the profile table, EDA insights and model summary. Close with
    the **Knowledge Assistant**, asking "What is precision?" to show the
    local RAG knowledge base in action.
