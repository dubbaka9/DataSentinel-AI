from app.models.domain import AgentFinding, Incident


def investigate(incident: Incident) -> AgentFinding:
    ids = {e.id for e in incident.evidence}
    chain = [x for x in ["schema_change", "spark_failure", "dbt_failure", "quality_alert"] if x in ids]
    return AgentFinding(
        agent="LineageAgent",
        hypothesis="Observed failure propagated from upstream schema into downstream transformation and quality checks.",
        evidence_ids=chain,
        proposed_actions=["Trace impacted downstream assets", "Block unrelated remediation"],
    )
