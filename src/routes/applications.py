import logging
from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from src import db
from src.llm.gemini_client import LLMApiError, LLMParsingError, extract_application
from src.models import ApplicationStatus
from src.templating import templates
from src.utils import parse_optional_int

logger = logging.getLogger("job_application_tracker")

router = APIRouter()


@router.get("/")
def index(request: Request):
    applications = db.list_applications()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "applications": applications,
            "statuses": list(ApplicationStatus),
        },
    )


@router.post("/applications/parse")
def parse_application(request: Request, text: str = Form(...), job_post_url: str = Form("")):
    text = text.strip()
    job_post_url = job_post_url.strip()

    if not text:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "applications": db.list_applications(),
                "statuses": list(ApplicationStatus),
                "parse_error": "Please enter application details before saving.",
            },
        )

    company = ""
    role = ""
    parse_notice = None
    try:
        parsed = extract_application(text)
        company = parsed.company
        role = parsed.role
    except (LLMApiError, LLMParsingError) as exc:
        logger.warning("Gemini parsing failed for input %r: %s", text, exc)
        parse_notice = "Could not parse automatically — please fill in manually."

    return templates.TemplateResponse(
        request,
        "confirm_add.html",
        {
            "company": company,
            "role": role,
            "job_post_url": job_post_url,
            "source_text": text,
            "today": date.today().isoformat(),
            "statuses": list(ApplicationStatus),
            "default_status": ApplicationStatus.APPLIED.value,
            "parse_notice": parse_notice,
        },
    )


@router.post("/applications")
def create_application(
    company: str = Form(...),
    role: str = Form(...),
    job_post_url: str = Form(""),
    source_text: str = Form(""),
    status: str = Form(ApplicationStatus.APPLIED.value),
    total_rounds: str = Form(""),
    current_round: str = Form(""),
    feedback: str = Form(""),
):
    db.create_application(
        company=company.strip(),
        role=role.strip(),
        job_post_url=job_post_url.strip() or None,
        source_text=source_text.strip() or None,
        status=status,
        total_rounds=parse_optional_int(total_rounds),
        current_round=parse_optional_int(current_round),
        feedback=feedback.strip() or None,
    )
    return RedirectResponse(url="/", status_code=303)


@router.post("/applications/{application_id}/status")
def update_application_status(application_id: int, status: ApplicationStatus = Form(...)):
    db.update_status(application_id, status.value)
    return RedirectResponse(url="/", status_code=303)


@router.post("/applications/{application_id}/details")
def update_application_details(
    application_id: int,
    total_rounds: str = Form(""),
    current_round: str = Form(""),
    feedback: str = Form(""),
):
    db.update_details(
        application_id,
        total_rounds=parse_optional_int(total_rounds),
        current_round=parse_optional_int(current_round),
        feedback=feedback.strip() or None,
    )
    return RedirectResponse(url="/", status_code=303)
