from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    detail: str


class DatasetOut(BaseModel):
    id: str
    original_filename: str
    n_rows: int
    n_cols: int
    columns: list[str]
    created_at: str
    is_cleaned: bool


class AskRequest(BaseModel):
    question: str


class SQLRequest(BaseModel):
    question: Optional[str] = None
    sql: Optional[str] = None


class ChartRequest(BaseModel):
    chart_type: str
    x: Optional[str] = None
    y: Optional[str] = None
    bins: int = 10


class TrainRequest(BaseModel):
    dataset_id: str
    target: Optional[str] = None
    feature_columns: list[str]
    problem_type: str
    algorithm: str
    test_size: float = 0.2
    random_state: int = 42
    n_clusters: int = 3
    tune: bool = False


class PredictRequest(BaseModel):
    input: dict[str, Any]


class KnowledgeRequest(BaseModel):
    question: str


class ReportRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    dataset_id: str
    model_id: Optional[str] = None
