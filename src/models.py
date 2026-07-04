from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class ParsedApplication(BaseModel):
    company: str
    role: str


class ApplicationCreate(BaseModel):
    company: str
    role: str
    job_post_url: Optional[str] = None
    source_text: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    total_rounds: Optional[int] = None
    current_round: Optional[int] = None
    feedback: Optional[str] = None


class StatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationOut(BaseModel):
    id: int
    company: str
    role: str
    date_applied: str
    status: ApplicationStatus
    job_post_url: Optional[str] = None
    source_text: Optional[str] = None
    total_rounds: Optional[int] = None
    current_round: Optional[int] = None
    feedback: Optional[str] = None
