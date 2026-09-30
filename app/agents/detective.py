from app.models.domain import AgentFinding, Incident


def investigate(incident: Incident) -> AgentFinding:
    ids = {e.id for e in incident.evidence}
    hypothesis = "Failure sequence is consistent with an upstream change preceding the first pipeline error."
    evidence = [i for i in ["deployment_event", "schema_change", "spark_failure"] if i in ids]
    return AgentFinding(
        agent="DetectiveAgent",
        hypothesis=hypothesis,
        evidence_ids=evidence,
        proposed_actions=["Correlate deployment and first-failure timestamps", "Inspect schema diff"],
    )
