import httpx
from app.models.domain import AgentFinding, Incident, ModelDiagnosis
from app.providers.base import DiagnosisProvider


class GeminiProvider(DiagnosisProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def diagnose(self, incident: Incident, findings: list[AgentFinding]) -> ModelDiagnosis:
        evidence_text = "\n".join(f"- {e.id}: {e.summary}" for e in incident.evidence)
        prompt = (
            "Diagnose this data pipeline incident using ONLY the supplied evidence. "
            "State the most likely root cause and a safe remediation. Do not invent facts.\n\n"
            f"Evidence:\n{evidence_text}"
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return ModelDiagnosis(
            provider=f"gemini:{self.model}",
            root_cause=text.strip(),
            evidence_ids=[e.id for e in incident.evidence],
            remediation="Use the generated recommendation only after deterministic risk-policy evaluation.",
        )
