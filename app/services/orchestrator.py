from __future__ import annotations

from datetime import datetime, timezone
from app.agents import data_agent, detective, lineage_agent
from app.core.config import Settings
from app.models.domain import Incident, IncidentStatus
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockGeminiProvider, MockLlamaProvider
from app.providers.ollama import OllamaLlamaProvider
from app.services.evidence_graph import EvidenceGraph
from app.services.policy import RemediationPolicy
from app.services.risk_engine import RiskEngine
from app.services.scoring import ConfidenceScorer
from app.services.store import IncidentStore
from app.services.validator import ValidationService


class IncidentOrchestrator:
    def __init__(self, settings: Settings, store: IncidentStore):
        self.settings = settings
        self.store = store
        self.graph = EvidenceGraph()
        self.scorer = ConfidenceScorer()
        self.risk_engine = RiskEngine()
        self.policy = RemediationPolicy()
        self.validator = ValidationService()

    def _providers(self):
        if self.settings.model_mode.lower() == "live":
            providers = []
            if self.settings.gemini_api_key:
                providers.append(GeminiProvider(self.settings.gemini_api_key, self.settings.gemini_model))
            providers.append(OllamaLlamaProvider(self.settings.ollama_base_url, self.settings.ollama_model))
            return providers
        return [MockGeminiProvider(), MockLlamaProvider()]

    async def investigate(self, incident: Incident) -> Incident:
        incident.status = IncidentStatus.investigating
        incident.findings = [
            detective.investigate(incident),
            data_agent.investigate(incident),
            lineage_agent.investigate(incident),
        ]
        graph = self.graph.build(incident)
        incident.audit_log.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "event": "evidence_graph_built",
            "graph": self.graph.summarize(graph),
        })

        incident.diagnoses = []
        for provider in self._providers():
            incident.diagnoses.append(await provider.diagnose(incident, incident.findings))

        incident.confidence = self.scorer.score(incident, incident.diagnoses)
        best = max(
            incident.diagnoses,
            key=lambda d: len(set(d.evidence_ids) & {e.id for e in incident.evidence}),
        )
        incident.root_cause = best.root_cause
        incident.risk = self.risk_engine.assess(incident)
        incident.decision = self.policy.decide(incident)

        if incident.decision.action == "REQUEST_APPROVAL":
            incident.status = IncidentStatus.awaiting_approval
        elif incident.decision.action in {"BLOCK", "ESCALATE"}:
            incident.status = IncidentStatus.escalated
        elif incident.decision.allowed:
            incident.status = IncidentStatus.remediating
            incident.validation = self.validator.validate(incident)
            incident.status = IncidentStatus.resolved if incident.validation["passed"] else IncidentStatus.rolled_back

        incident.audit_log.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "event": "investigation_completed",
            "confidence": incident.confidence.final,
            "risk": incident.risk.score,
            "decision": incident.decision.action,
        })
        return self.store.save(incident)

    async def replay(self, incident: Incident) -> Incident:
        clone = incident.model_copy(deep=True)
        clone.findings = []
        clone.diagnoses = []
        clone.root_cause = None
        clone.confidence = None
        clone.risk = None
        clone.decision = None
        clone.validation = None
        clone.audit_log.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "event": "replay_started",
        })
        return await self.investigate(clone)
