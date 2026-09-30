from app.models.domain import Incident, RiskLevel, RemediationDecision


class RemediationPolicy:
    def decide(self, incident: Incident) -> RemediationDecision:
        if not incident.risk or not incident.confidence:
            return RemediationDecision(action="ESCALATE", allowed=False, reason="Missing confidence or risk assessment")
        if incident.confidence.final < 0.65:
            return RemediationDecision(action="ESCALATE", allowed=False, reason="Diagnosis confidence too low")
        if incident.risk.level == RiskLevel.high:
            return RemediationDecision(action="BLOCK", allowed=False, reason="High-risk remediation requires engineer review")
        if incident.risk.level == RiskLevel.medium:
            return RemediationDecision(action="REQUEST_APPROVAL", allowed=False, reason="Medium-risk remediation requires human approval")
        return RemediationDecision(action="AUTO_REMEDIATE", allowed=True, reason="Low-risk remediation passed policy gates")
