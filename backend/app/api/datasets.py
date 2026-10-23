from __future__ import annotations

import json

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agents import cleaning, eda as eda_agent, profiling, visualization
from app.database import db
from app.schemas.common import ChartRequest
from app.services import dataset_service

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        row = await dataset_service.save_upload(file)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": row["id"], "original_filename": row["original_filename"],
        "n_rows": row["n_rows"], "n_cols": row["n_cols"],
        "columns": json.loads(row["columns_json"]), "created_at": row["created_at"], "is_cleaned": False,
    }


@router.get("")
def list_all():
    rows = db.list_datasets()
    return [
        {"id": r["id"], "original_filename": r["original_filename"], "n_rows": r["n_rows"], "n_cols": r["n_cols"],
         "columns": json.loads(r["columns_json"]), "created_at": r["created_at"], "is_cleaned": bool(r["is_cleaned"])}
        for r in rows
    ]


@router.get("/{dataset_id}")
def get_one(dataset_id: str):
    try:
        r = dataset_service.get_dataset_meta(dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": r["id"], "original_filename": r["original_filename"], "n_rows": r["n_rows"], "n_cols": r["n_cols"],
            "columns": json.loads(r["columns_json"]), "created_at": r["created_at"], "is_cleaned": bool(r["is_cleaned"])}


@router.get("/{dataset_id}/preview")
def preview(dataset_id: str, limit: int = 50):
    df = _load(dataset_id)
    return {"columns": list(df.columns.astype(str)), "rows": df.head(limit).fillna("").to_dict(orient="records")}


@router.get("/{dataset_id}/profile")
def profile(dataset_id: str):
    df = _load(dataset_id)
    return profiling.profile_dataset(df)


@router.post("/{dataset_id}/clean")
def clean(dataset_id: str, steps: list[cleaning.CleaningStep]):
    df = _load(dataset_id)
    cleaned_df, log = cleaning.apply_cleaning(df, steps)
    dataset_service.save_working_df(dataset_id, cleaned_df)
    db.update_dataset_cleaning(dataset_id, log, int(cleaned_df.shape[0]), int(cleaned_df.shape[1]), list(cleaned_df.columns.astype(str)))
    return {"cleaning_log": log, "n_rows": int(cleaned_df.shape[0]), "n_cols": int(cleaned_df.shape[1]), "preview": cleaned_df.head(20).fillna("").to_dict(orient="records")}


@router.get("/{dataset_id}/cleaning-log")
def cleaning_log(dataset_id: str):
    try:
        meta = dataset_service.get_dataset_meta(dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return json.loads(meta["cleaning_log_json"] or "[]")


@router.get("/{dataset_id}/eda")
def eda_endpoint(dataset_id: str):
    df = _load(dataset_id)
    return eda_agent.run_eda(df)


@router.post("/{dataset_id}/visualize")
def visualize(dataset_id: str, req: ChartRequest):
    df = _load(dataset_id)
    try:
        return visualization.build_chart(df, req.chart_type, req.x, req.y, req.bins)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _load(dataset_id: str):
    try:
        return dataset_service.load_working_df(dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
