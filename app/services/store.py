from __future__ import annotations

from pathlib import Path
from app.models.domain import Incident


class IncidentStore:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, incident: Incident) -> Incident:
        path = self.root / f"{incident.id}.json"
        path.write_text(incident.model_dump_json(indent=2), encoding="utf-8")
        return incident

    def load(self, incident_id: str) -> Incident:
        path = self.root / f"{incident_id}.json"
        if not path.exists():
            raise FileNotFoundError(incident_id)
        return Incident.model_validate_json(path.read_text(encoding="utf-8"))

    def list_ids(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))
