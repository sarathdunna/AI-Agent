"""NL -> SQL agent. Uses LLM if available, else a rule-based fallback. Executes via DuckDB
against the dataset registered as table 'data'. Read-only, allowlist-enforced."""
from __future__ import annotations

import duckdb
import pandas as pd

from app.services.llm_provider import get_llm_provider
from app.utils.security import validate_readonly_sql, UnsafeSQLError


def _rule_based_sql(question: str, df: pd.DataFrame) -> str:
    q = question.lower()
    cols = list(df.columns)
    if "how many rows" in q or "count of rows" in q or "number of rows" in q:
        return "SELECT COUNT(*) AS row_count FROM data"
    if "columns" in q and ("list" in q or "what" in q):
        return "SELECT * FROM data LIMIT 5"
    for col in cols:
        if col.lower() in q and ("average" in q or "mean" in q):
            return f'SELECT AVG("{col}") AS average_{col} FROM data'
        if col.lower() in q and ("max" in q or "highest" in q):
            return f'SELECT MAX("{col}") AS max_{col} FROM data'
        if col.lower() in q and ("min" in q or "lowest" in q):
            return f'SELECT MIN("{col}") AS min_{col} FROM data'
    return "SELECT * FROM data LIMIT 10"


def generate_sql(question: str, df: pd.DataFrame) -> tuple[str, str]:
    """Returns (sql, source) where source is 'llm' or 'rule_based'."""
    llm = get_llm_provider()
    schema = ", ".join(f"{c} ({df[c].dtype})" for c in df.columns)
    if llm.is_available():
        raw = llm.complete(
            system=(
                "You translate natural-language questions into a single read-only DuckDB SQL SELECT statement "
                "against a table named 'data'. Output ONLY the SQL, no explanation, no markdown fences. "
                "Never use DROP/DELETE/UPDATE/INSERT/ALTER/CREATE/TRUNCATE/ATTACH/COPY."
            ),
            prompt=f"Table 'data' columns: {schema}\nQuestion: {question}\nSQL:",
        )
        sql = raw.strip().strip("`").replace("sql\n", "").strip()
        if sql and not sql.lower().startswith("ai explanation unavailable"):
            return sql, "llm"
    return _rule_based_sql(question, df), "rule_based"


def run_sql(sql: str, df: pd.DataFrame) -> dict:
    validated = validate_readonly_sql(sql)
    con = duckdb.connect(database=":memory:")
    con.register("data", df)
    try:
        result_df = con.execute(validated).fetchdf()
    finally:
        con.close()
    return {
        "columns": list(result_df.columns.astype(str)),
        "rows": result_df.head(500).to_dict(orient="records"),
        "row_count": int(len(result_df)),
    }
