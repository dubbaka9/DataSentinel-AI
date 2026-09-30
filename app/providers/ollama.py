import httpx
from app.models.domain import AgentFinding, Incident, ModelDiagnosis
from app.providers.base import DiagnosisProvider


class OllamaLlamaProvider(DiagnosisProvider):
    name = "ollama-llama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def diagnose(self, incident: Incident, findings: list[AgentFinding]) -> ModelDiagnosis:
        evidence_text = "\n".join(f"- {e.id}: {e.summary}" for e in incident.evidence)
        prompt = (
            "You are a data reliability investigator. Use only supplied evidence. "
            "Return a concise root cause and remediation.\n\nEvidence:\n" + evidence_text
        )
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            text = response.json().get("response", "")
        return ModelDiagnosis(
            provider=f"ollama:{self.model}",
            root_cause=text.strip() or "No diagnosis returned",
            evidence_ids=[e.id for e in incident.evidence],
            remediation="Review model output and execute only through the policy-controlled remediation workflow.",
        )
