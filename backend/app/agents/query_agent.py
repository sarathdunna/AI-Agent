"""Natural-language data query agent: routes a question to DuckDB SQL and returns
answer + table + chart suggestion + code + explanation."""
from __future__ import annotations

import pandas as pd

from app.agents import sql_agent, visualization
from app.services.llm_provider import get_llm_provider


def answer_question(question: str, df: pd.DataFrame) -> dict:
    sql, source = sql_agent.generate_sql(question, df)
    try:
        result = sql_agent.run_sql(sql, df)
        error = None
    except Exception as exc:  # noqa: BLE001
        result = {"columns": [], "rows": [], "row_count": 0}
        error = str(exc)

    chart = None
    if not error and result["rows"] and len(result["columns"]) >= 2:
        cols = result["columns"]
        try:
            sample = pd.DataFrame(result["rows"])
            if pd.api.types.is_numeric_dtype(sample[cols[1]]):
                chart = {
                    "chart_type": "bar",
                    "data": [{"name": str(r[cols[0]]), "value": r[cols[1]]} for r in result["rows"][:20]],
                }
        except Exception:  # noqa: BLE001
            chart = None

    llm = get_llm_provider()
    if error:
        explanation = f"The generated query could not run safely: {error}"
    elif llm.is_available():
        explanation = llm.complete(
            system="Explain the query result in 2-3 plain-English sentences using ONLY the given data. Do not invent numbers.",
            prompt=f"Question: {question}\nSQL used: {sql}\nResult sample: {result['rows'][:10]}",
        )
    else:
        explanation = f"Query returned {result['row_count']} row(s). (Enable an LLM key for a richer narrative explanation.)"

    return {
        "question": question,
        "sql": sql,
        "sql_source": source,
        "columns": result["columns"],
        "rows": result["rows"],
        "row_count": result["row_count"],
        "chart": chart,
        "explanation": explanation,
        "error": error,
    }
