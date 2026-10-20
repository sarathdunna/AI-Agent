from __future__ import annotations

import json

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.database import db
from app.ml import algorithm_selector, explainability, problem_id, tuning, training, prediction
from app.schemas.common import PredictRequest, TrainRequest
from app.services import dataset_service

router = APIRouter(prefix="/ml", tags=["ml"])


@router.get("/problem-type")
def get_problem_type(dataset_id: str, target: str | None = None):
    df = dataset_service.load_working_df(dataset_id)
    return problem_id.identify_problem_type(df, target)


@router.get("/algorithms")
def get_algorithms(problem_type: str):
    return algorithm_selector.recommend_algorithms(problem_type)


@router.post("/train")
def train(req: TrainRequest):
    try:
        df = dataset_service.load_working_df(req.dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        if req.tune and req.problem_type != "clustering":
            tuned = tuning.tune_model(df, req.target, req.feature_columns, req.problem_type, req.algorithm, req.test_size, req.random_state)
            result = training.train_model(df, req.target, req.feature_columns, req.problem_type, req.algorithm, req.test_size, req.random_state, req.n_clusters)
            result["tuning"] = {"before": tuned["before"], "after": tuned["after"], "best_params": tuned.get("best_params", {}), "tuned": tuned["tuned"]}
        else:
            result = training.train_model(df, req.target, req.feature_columns, req.problem_type, req.algorithm, req.test_size, req.random_state, req.n_clusters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown column: {exc}") from exc

    db.insert_model({
        "id": result["model_id"], "dataset_id": req.dataset_id, "target": req.target,
        "problem_type": req.problem_type, "algorithm": req.algorithm,
        "feature_columns_json": json.dumps(req.feature_columns),
        "metrics_json": json.dumps(result["metrics"]), "params_json": json.dumps(result.get("tuning", {}).get("best_params", {})),
        "model_path": result["model_path"], "created_at": db.now_iso(),
    })
    return {k: v for k, v in result.items() if k != "model_path"}


@router.get("/models")
def list_models(dataset_id: str | None = None):
    rows = db.list_models()
    out = []
    for r in rows:
        if dataset_id and r["dataset_id"] != dataset_id:
            continue
        out.append({
            "id": r["id"], "dataset_id": r["dataset_id"], "target": r["target"], "problem_type": r["problem_type"],
            "algorithm": r["algorithm"], "feature_columns": json.loads(r["feature_columns_json"]),
            "metrics": json.loads(r["metrics_json"]), "created_at": r["created_at"],
        })
    return out


@router.get("/models/{model_id}")
def get_model(model_id: str):
    r = db.get_model(model_id)
    if r is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return {
        "id": r["id"], "dataset_id": r["dataset_id"], "target": r["target"], "problem_type": r["problem_type"],
        "algorithm": r["algorithm"], "feature_columns": json.loads(r["feature_columns_json"]),
        "metrics": json.loads(r["metrics_json"]), "created_at": r["created_at"],
    }


@router.post("/models/{model_id}/predict")
def predict(model_id: str, req: PredictRequest):
    r = db.get_model(model_id)
    if r is None:
        raise HTTPException(status_code=404, detail="Model not found")
    bundle = training.load_model(r["model_path"])
    try:
        return prediction.predict_single(bundle, req.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/models/{model_id}/predict-batch")
async def predict_batch(model_id: str, file: UploadFile = File(...)):
    r = db.get_model(model_id)
    if r is None:
        raise HTTPException(status_code=404, detail="Model not found")
    bundle = training.load_model(r["model_path"])
    content = await file.read()
    import io
    try:
        df = pd.read_csv(io.BytesIO(content)) if (file.filename or "").lower().endswith(".csv") else pd.read_excel(io.BytesIO(content))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Could not parse uploaded file") from exc
    try:
        out = prediction.predict_batch(bundle, df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"columns": list(out.columns.astype(str)), "rows": out.head(500).fillna("").to_dict(orient="records"), "row_count": int(len(out))}


@router.get("/models/{model_id}/importance")
def importance(model_id: str):
    r = db.get_model(model_id)
    if r is None:
        raise HTTPException(status_code=404, detail="Model not found")
    bundle = training.load_model(r["model_path"])
    df = dataset_service.load_working_df(r["dataset_id"])
    feature_columns = json.loads(r["feature_columns_json"])
    X = df[feature_columns]
    y = df[r["target"]] if r["target"] and r["target"] in df.columns else None
    return explainability.explain_model(bundle["pipeline"], X, y)
