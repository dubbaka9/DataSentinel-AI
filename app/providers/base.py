from abc import ABC, abstractmethod
from app.models.domain import AgentFinding, Incident, ModelDiagnosis


class DiagnosisProvider(ABC):
    name: str

    @abstractmethod
    async def diagnose(self, incident: Incident, findings: list[AgentFinding]) -> ModelDiagnosis:
        raise NotImplementedError
