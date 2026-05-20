import json
from pathlib import Path
from backend.models.incident import IncidentAnalysisRequest, IncidentAnalysisResponse, SampleIncident
from backend.prompts.templates import INCIDENT_ANALYSIS_SYSTEM_PROMPT, INCIDENT_ANALYSIS_PROMPT_TEMPLATE
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_DATA_FILE = Path(__file__).parent.parent / "data" / "sample_incidents.json"


class IncidentService:
    def __init__(self, ai_service, ai_mode: str):
        self._ai = ai_service
        self.ai_mode = ai_mode

    def load_samples(self) -> list[SampleIncident]:
        data = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
        return [SampleIncident(**item) for item in data]

    def analyze(self, request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
        logger.info("Analyzing incident: '%s' (%d users)", request.title, request.affected_users)

        prompt = INCIDENT_ANALYSIS_PROMPT_TEMPLATE.format(
            title=request.title,
            description=request.description,
            affected_users=request.affected_users,
        )

        try:
            result = self._ai.structured_completion(
                prompt=prompt,
                system=INCIDENT_ANALYSIS_SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.error("AI structured completion failed: %s", exc)
            raise

        # Clamp confidence to valid range
        result["confidence_score"] = max(0.0, min(1.0, float(result.get("confidence_score", 0.75))))

        logger.info(
            "Analysis complete | severity=%s | category=%s | group=%s",
            result.get("severity"),
            result.get("category"),
            result.get("assignment_group"),
        )

        return IncidentAnalysisResponse(**result, ai_mode=self.ai_mode)
