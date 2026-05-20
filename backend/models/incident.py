from pydantic import BaseModel, Field
from typing import Optional


class IncidentAnalysisRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Short incident title")
    description: str = Field(..., min_length=10, description="Full incident description")
    affected_users: Optional[int] = Field(default=1, ge=0, description="Number of affected users")


class IncidentAnalysisResponse(BaseModel):
    summary: str
    category: str
    severity: str           # P1, P2, P3, P4
    severity_label: str     # Critical, High, Medium, Low
    assignment_group: str
    troubleshooting_steps: list[str]
    estimated_resolution_time: str
    confidence_score: float  # 0.0 – 1.0
    ai_mode: str            # "ollama" or "mock"


class SampleIncident(BaseModel):
    id: str
    title: str
    description: str
    affected_users: int
    category_hint: str
