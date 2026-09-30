from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


class RiskLevel(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"


class IncidentStatus(str, Enum):
    detected = "DETECTED"
    investigating = "INVESTIGATING"
    awaiting_approval = "AWAITING_APPROVAL"
    remediating = "REMEDIATING"
    resolved = "RESOLVED"
    escalated = "ESCALATED"
    rolled_back = "ROLLED_BACK"


class Evidence(BaseModel):
    id: str
    kind: str
    source: str
    timestamp: datetime
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    reliability: float = Field(default=1.0, ge=0, le=1)


class AgentFinding(BaseModel):
    agent: str
    hypothesis: str
    evidence_ids: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)


class ModelDiagnosis(BaseModel):
    provider: str
    root_cause: str
    evidence_ids: list[str] = Field(default_factory=list)
    remediation: str


class ConfidenceBreakdown(BaseModel):
    evidence_coverage: float
    temporal_consistency: float
    lineage_consistency: float
    model_agreement: float
    final: float


class RiskAssessment(BaseModel):
    level: RiskLevel
    score: int = Field(ge=0, le=100)
    requires_human_approval: bool
    reasons: list[str]


class RemediationDecision(BaseModel):
    action: str
    allowed: bool
    reason: str


class Incident(BaseModel):
    id: str
    title: str
    severity: Severity
    status: IncidentStatus = IncidentStatus.detected
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pipeline: str
    asset: str
    symptoms: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Evidence] = Field(default_factory=list)
    findings: list[AgentFinding] = Field(default_factory=list)
    diagnoses: list[ModelDiagnosis] = Field(default_factory=list)
    root_cause: str | None = None
    confidence: ConfidenceBreakdown | None = None
    risk: RiskAssessment | None = None
    decision: RemediationDecision | None = None
    validation: dict[str, Any] | None = None
    audit_log: list[dict[str, Any]] = Field(default_factory=list)
