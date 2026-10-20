from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.agents import pandas_agent, query_agent, sql_agent, insight_agent
from app.schemas.common import AskRequest, SQLRequest
from app.services import dataset_service
from app.utils.security import UnsafeSQLError

router = APIRouter(prefix="/datasets", tags=["query"])


@router.post("/{dataset_id}/ask")
def ask(dataset_id: str, req: AskRequest):
    df = _load(dataset_id)
    return query_agent.answer_question(req.question, df)


@router.post("/{dataset_id}/sql")
def sql_endpoint(dataset_id: str, req: SQLRequest):
    df = _load(dataset_id)
    if req.sql:
        try:
            result = sql_agent.run_sql(req.sql, df)
        except UnsafeSQLError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"sql": req.sql, "sql_source": "user", **result}
    if not req.question:
        raise HTTPException(status_code=400, detail="Provide either 'sql' or 'question'")
    sql, source = sql_agent.generate_sql(req.question, df)
    try:
        result = sql_agent.run_sql(sql, df)
    except UnsafeSQLError as exc:
        raise HTTPException(status_code=400, detail=f"Generated SQL was rejected: {exc}") from exc
    return {"sql": sql, "sql_source": source, **result}


@router.post("/{dataset_id}/pandas-op")
def pandas_op(dataset_id: str, req: pandas_agent.PandasOpRequest):
    df = _load(dataset_id)
    try:
        return pandas_agent.run_pandas_op(df, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{dataset_id}/insights")
def insights(dataset_id: str):
    df = _load(dataset_id)
    return {"facts": insight_agent.extract_facts(df)}


def _load(dataset_id: str):
    try:
        return dataset_service.load_working_df(dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
