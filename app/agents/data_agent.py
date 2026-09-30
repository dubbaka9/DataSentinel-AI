from app.models.domain import AgentFinding, Incident


def investigate(incident: Incident) -> AgentFinding:
    schema = next((e for e in incident.evidence if e.id == "schema_change"), None)
    if schema:
        hypothesis = f"Schema contract drift detected: {schema.summary}"
        evidence = ["schema_change", "quality_alert"]
    else:
        hypothesis = "No explicit schema drift evidence found; inspect data-quality metrics."
        evidence = [e.id for e in incident.evidence if e.kind == "quality"]
    return AgentFinding(
        agent="DataAgent",
        hypothesis=hypothesis,
        evidence_ids=[e for e in evidence if any(x.id == e for x in incident.evidence)],
        proposed_actions=["Validate required columns", "Compare null and row-count metrics"],
    )
