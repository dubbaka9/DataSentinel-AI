from app.models.domain import ConfidenceBreakdown, RiskLevel
from app.services.demo import build_demo_incident
from app.services.risk_engine import RiskEngine


def test_demo_is_medium_risk():
    incident = build_demo_incident()
    incident.confidence = ConfidenceBreakdown(
        evidence_coverage=1,
        temporal_consistency=1,
        lineage_consistency=1,
        model_agreement=0.9,
        final=0.98,
    )
    risk = RiskEngine().assess(incident)
    assert risk.level == RiskLevel.medium
    assert risk.requires_human_approval is True
