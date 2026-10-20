"""PDF report generator using reportlab."""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.core.config import get_settings
from app.database import db


def generate_report(dataset_id: str, profile: dict, eda: dict, model_id: str | None = None) -> Path:
    settings = get_settings()
    out_path = settings.REPORTS_DIR / f"report_{dataset_id}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out_path), pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    story.append(Paragraph("Data Analyst + ML Agent — Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))

    meta = db.get_dataset(dataset_id)
    story.append(Paragraph(f"Dataset: {meta['original_filename'] if meta else dataset_id}", styles["Heading2"]))
    story.append(Paragraph(f"Rows: {profile['n_rows']} &nbsp;&nbsp; Columns: {profile['n_cols']} &nbsp;&nbsp; Duplicate rows: {profile['duplicate_rows']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Column Profile", styles["Heading2"]))
    table_data = [["Column", "Type", "Missing %", "Unique"]]
    for c in profile["columns"][:30]:
        table_data.append([c["name"], c["inferred_type"], f"{c['missing_pct']}%", str(c["unique_count"])])
    t = Table(table_data, hAlign="LEFT")
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0"))]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("EDA Insights", styles["Heading2"]))
    for insight in eda.get("insights", []):
        story.append(Paragraph(f"• {insight}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if model_id:
        model_row = db.get_model(model_id)
        if model_row:
            story.append(Paragraph("Model Summary", styles["Heading2"]))
            metrics = json.loads(model_row["metrics_json"] or "{}")
            story.append(Paragraph(f"Algorithm: {model_row['algorithm']} ({model_row['problem_type']})", styles["Normal"]))
            story.append(Paragraph(f"Target: {model_row['target']}", styles["Normal"]))
            for k, v in metrics.items():
                if k in ("explanations", "confusion_matrix"):
                    continue
                story.append(Paragraph(f"{k}: {v}", styles["Normal"]))

    doc.build(story)
    return out_path
