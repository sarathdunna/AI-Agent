from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.agents import eda as eda_agent, profiling
from app.analytics import dashboard
from app.rag import knowledge_agent
from app.schemas.common import KnowledgeRequest, ReportRequest
from app.services import dataset_service, report_generator

router = APIRouter(tags=["misc"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/datasets/{dataset_id}/dashboard")
def get_dashboard(dataset_id: str):
    try:
        df = dataset_service.load_working_df(dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return dashboard.build_dashboard(dataset_id, df)


@router.post("/knowledge/ask")
def knowledge_ask(req: KnowledgeRequest):
    return knowledge_agent.ask_knowledge(req.question)


@router.post("/reports/generate")
def generate_report(req: ReportRequest):
    try:
        df = dataset_service.load_working_df(req.dataset_id)
    except dataset_service.DatasetValidationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    profile = profiling.profile_dataset(df)
    eda = eda_agent.run_eda(df)
    path = report_generator.generate_report(req.dataset_id, profile, eda, req.model_id)
    return FileResponse(str(path), media_type="application/pdf", filename=path.name)
