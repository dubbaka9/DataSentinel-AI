import pytest
from app.core.config import Settings
from app.models.domain import IncidentStatus
from app.services.demo import build_demo_incident
from app.services.orchestrator import IncidentOrchestrator
from app.services.store import IncidentStore


@pytest.mark.asyncio
async def test_demo_investigation_requires_approval(tmp_path):
    settings = Settings(model_mode="mock", incident_store=str(tmp_path))
    store = IncidentStore(str(tmp_path))
    incident = store.save(build_demo_incident())
    result = await IncidentOrchestrator(settings, store).investigate(incident)
    assert result.root_cause
    assert result.confidence is not None
    assert result.risk is not None
    assert result.decision.action == "REQUEST_APPROVAL"
    assert result.status == IncidentStatus.awaiting_approval
