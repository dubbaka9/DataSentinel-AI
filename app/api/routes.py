from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.models.domain import Incident
from app.services.demo import build_demo_incident
from app.services.orchestrator import IncidentOrchestrator
from app.services.store import IncidentStore

router = APIRouter(prefix="/incidents", tags=["incidents"])
settings = get_settings()
store = IncidentStore(settings.incident_store)
orchestrator = IncidentOrchestrator(settings, store)


@router.get("")
def list_incidents() -> dict:
    return {"incident_ids": store.list_ids()}


@router.post("/demo", response_model=Incident)
def create_demo_incident() -> Incident:
    return store.save(build_demo_incident())


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: str) -> Incident:
    try:
        return store.load(incident_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("/{incident_id}/investigate", response_model=Incident)
async def investigate_incident(incident_id: str) -> Incident:
    try:
        incident = store.load(incident_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await orchestrator.investigate(incident)


@router.post("/{incident_id}/replay", response_model=Incident)
async def replay_incident(incident_id: str) -> Incident:
    try:
        incident = store.load(incident_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await orchestrator.replay(incident)
