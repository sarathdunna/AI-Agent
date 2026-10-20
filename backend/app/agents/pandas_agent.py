"""Pandas agent — a fixed set of safe analytical operations (no arbitrary eval of LLM code).
Each op also returns the equivalent readable pandas code as a string for transparency."""
from __future__ import annotations

from typing import Any, Literal, Optional

import pandas as pd
from pydantic import BaseModel


class PandasOpRequest(BaseModel):
    op: Literal["groupby", "pivot", "filter", "aggregate", "correlate", "describe"]
    columns: Optional[list[str]] = None
    group_by: Optional[str] = None
    agg_col: Optional[str] = None
    agg_func: Optional[str] = "mean"  # mean|sum|count|min|max|median
    pivot_index: Optional[str] = None
    pivot_columns: Optional[str] = None
    pivot_values: Optional[str] = None
    filter_col: Optional[str] = None
    filter_op: Optional[str] = None  # ==, !=, >, <, >=, <=, contains
    filter_value: Optional[Any] = None


ALLOWED_AGG = {"mean", "sum", "count", "min", "max", "median", "std"}
ALLOWED_FILTER_OPS = {"==", "!=", ">", "<", ">=", "<=", "contains"}


def run_pandas_op(df: pd.DataFrame, req: PandasOpRequest) -> dict:
    if req.op == "groupby":
        if not req.group_by or not req.agg_col:
            raise ValueError("group_by and agg_col are required")
        if req.agg_func not in ALLOWED_AGG:
            raise ValueError(f"agg_func must be one of {ALLOWED_AGG}")
        result = df.groupby(req.group_by)[req.agg_col].agg(req.agg_func).reset_index()
        code = f'df.groupby("{req.group_by}")["{req.agg_col}"].agg("{req.agg_func}").reset_index()'

    elif req.op == "pivot":
        if not (req.pivot_index and req.pivot_columns and req.pivot_values):
            raise ValueError("pivot_index, pivot_columns and pivot_values are required")
        result = pd.pivot_table(df, index=req.pivot_index, columns=req.pivot_columns, values=req.pivot_values, aggfunc=req.agg_func or "mean").reset_index()
        code = f'pd.pivot_table(df, index="{req.pivot_index}", columns="{req.pivot_columns}", values="{req.pivot_values}", aggfunc="{req.agg_func}").reset_index()'

    elif req.op == "filter":
        if not (req.filter_col and req.filter_op and req.filter_op in ALLOWED_FILTER_OPS):
            raise ValueError(f"filter_col and a valid filter_op {ALLOWED_FILTER_OPS} are required")
        if req.filter_op == "contains":
            result = df[df[req.filter_col].astype(str).str.contains(str(req.filter_value), case=False, na=False)]
            code = f'df[df["{req.filter_col}"].astype(str).str.contains("{req.filter_value}", case=False, na=False)]'
        else:
            result = df.query(f'`{req.filter_col}` {req.filter_op} @val', local_dict={"val": req.filter_value})
            code = f'df[df["{req.filter_col}"] {req.filter_op} {req.filter_value!r}]'

    elif req.op == "aggregate":
        cols = req.columns or df.select_dtypes(include="number").columns.tolist()
        if req.agg_func not in ALLOWED_AGG:
            raise ValueError(f"agg_func must be one of {ALLOWED_AGG}")
        result = df[cols].agg(req.agg_func).to_frame().T
        code = f'df[{cols}].agg("{req.agg_func}")'

    elif req.op == "correlate":
        cols = req.columns or df.select_dtypes(include="number").columns.tolist()
        result = df[cols].corr(numeric_only=True).reset_index()
        code = f'df[{cols}].corr()'

    elif req.op == "describe":
        cols = req.columns or list(df.columns)
        result = df[cols].describe(include="all").reset_index()
        code = f'df[{cols}].describe(include="all")'

    else:
        raise ValueError(f"Unsupported op '{req.op}'")

    result = result.head(500)
    return {
        "columns": [str(c) for c in result.columns],
        "rows": result.to_dict(orient="records"),
        "row_count": int(len(result)),
        "python_code": code,
    }
