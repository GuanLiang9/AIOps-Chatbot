from fastapi import APIRouter, Request, HTTPException
from backend.models.incident import IncidentAnalysisRequest, IncidentAnalysisResponse, SampleIncident
from backend.utils.logger import get_logger

router = APIRouter(prefix="/api/incidents", tags=["incidents"])
logger = get_logger(__name__)


@router.get("/samples", response_model=list[SampleIncident])
async def get_samples(request: Request):
    return request.app.state.incident_service.load_samples()


@router.post("/analyze", response_model=IncidentAnalysisResponse)
async def analyze_incident(payload: IncidentAnalysisRequest, request: Request):
    try:
        return request.app.state.incident_service.analyze(payload)
    except Exception as exc:
        logger.error("Incident analysis error: %s", exc)
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.post("/analyze-sample/{sample_id}", response_model=IncidentAnalysisResponse)
async def analyze_sample(sample_id: str, request: Request):
    samples = request.app.state.incident_service.load_samples()
    sample = next((s for s in samples if s.id == sample_id), None)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found")

    payload = IncidentAnalysisRequest(
        title=sample.title,
        description=sample.description,
        affected_users=sample.affected_users,
    )
    try:
        return request.app.state.incident_service.analyze(payload)
    except Exception as exc:
        logger.error("Sample incident analysis error: %s", exc)
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")
