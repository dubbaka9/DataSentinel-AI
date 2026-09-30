from __future__ import annotations

from app.models.domain import Incident, RiskAssessment, RiskLevel


class RiskEngine:
    """Deterministic remediation-risk policy. LLMs do not set this score."""

    def assess(self, incident: Incident) -> RiskAssessment:
        score = 10
        reasons: list[str] = []
        meta = incident.metadata

        downstream = int(meta.get("downstream_assets", 0))
        score += min(20, downstream * 3)
        if downstream:
            reasons.append(f"{downstream} downstream assets may be affected")

        if meta.get("changes_transformation_logic"):
            score += 20
            reasons.append("Proposed fix changes transformation logic")
        if meta.get("sensitive_data"):
            score += 25
            reasons.append("Pipeline contains sensitive or regulated data")
        if meta.get("data_loss_possible"):
            score += 30
            reasons.append("Remediation could cause irreversible data loss")
        if not meta.get("rollback_available", False):
            score += 15
            reasons.append("No tested rollback is available")
        if incident.confidence and incident.confidence.final < 0.75:
            score += 15
            reasons.append("Root-cause confidence is below 0.75")

        score = min(score, 100)
        if score < 40:
            level = RiskLevel.low
        elif score < 70:
            level = RiskLevel.medium
        else:
            level = RiskLevel.high

        return RiskAssessment(
            level=level,
            score=score,
            requires_human_approval=level != RiskLevel.low,
            reasons=reasons or ["No material remediation risks detected"],
        )
