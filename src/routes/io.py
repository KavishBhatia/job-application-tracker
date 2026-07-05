import datetime

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import Response

from src import db
from src.io_formats.csv_io import from_csv, to_csv
from src.io_formats.excel_io import from_excel, to_excel
from src.models import ApplicationStatus
from src.templating import templates
from src.utils import parse_optional_int

router = APIRouter()

VALID_STATUSES = {status.value for status in ApplicationStatus}


@router.get("/import-export")
def import_export_page(request: Request):
    return templates.TemplateResponse(request, "import_export.html", {})


@router.get("/export.csv")
def export_csv():
    content = to_csv(db.list_applications())
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )


@router.get("/export.xlsx")
def export_excel():
    content = to_excel(db.list_applications())
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=applications.xlsx"},
    )


@router.post("/import")
def import_applications(request: Request, file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    rows = from_excel(file.file) if filename.endswith(".xlsx") else from_csv(file.file)

    imported = 0
    skipped = 0
    rejected = 0

    for row in rows:
        company = (row.get("company") or "").strip()
        role = (row.get("role") or "").strip()
        status = (row.get("status") or "").strip() or ApplicationStatus.APPLIED.value
        date_applied = (row.get("date_applied") or "").strip() or datetime.date.today().isoformat()
        job_post_url = (row.get("job_post_url") or "").strip() or None
        source_text = (row.get("source_text") or "").strip() or None
        total_rounds = parse_optional_int(row.get("total_rounds"))
        current_round = parse_optional_int(row.get("current_round"))
        feedback = (str(row.get("feedback") or "")).strip() or None

        if not company or not role or status not in VALID_STATUSES:
            rejected += 1
            continue

        if db.application_exists(company, role, date_applied):
            skipped += 1
            continue

        db.insert_imported_row(
            company=company,
            role=role,
            date_applied=date_applied,
            status=status,
            job_post_url=job_post_url,
            source_text=source_text,
            total_rounds=total_rounds,
            current_round=current_round,
            feedback=feedback,
        )
        imported += 1

    summary = f"Imported: {imported}, Skipped as duplicates: {skipped}, Rejected: {rejected}"

    return templates.TemplateResponse(
        request,
        "import_export.html",
        {
            "import_summary": summary,
        },
    )
