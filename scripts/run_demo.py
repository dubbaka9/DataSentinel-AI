import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.services.demo import build_demo_incident
from app.services.orchestrator import IncidentOrchestrator
from app.services.store import IncidentStore


async def main():
    settings = get_settings()
    store = IncidentStore(settings.incident_store)
    incident = store.save(build_demo_incident())
    result = await IncidentOrchestrator(settings, store).investigate(incident)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
