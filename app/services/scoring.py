from __future__ import annotations

from difflib import SequenceMatcher
from app.models.domain import ConfidenceBreakdown, Incident, ModelDiagnosis


class ConfidenceScorer:
    def score(self, incident: Incident, diagnoses: list[ModelDiagnosis]) -> ConfidenceBreakdown:
        expected = {"deployment", "schema", "pipeline", "downstream"}
        present = set()
        for e in incident.evidence:
            if e.kind in {"deployment", "schema", "pipeline", "downstream", "quality"}:
                present.add("downstream" if e.kind == "quality" else e.kind)
        evidence_coverage = min(1.0, len(present & expected) / len(expected))

        ordered = sorted(incident.evidence, key=lambda e: e.timestamp)
        temporal_consistency = 1.0 if all(
            ordered[i].timestamp <= ordered[i + 1].timestamp for i in range(len(ordered) - 1)
        ) else 0.4

        ids = {e.id for e in incident.evidence}
        lineage_links = [
            ("schema_change", "spark_failure"),
            ("spark_failure", "dbt_failure"),
        ]
        valid_links = sum(1 for a, b in lineage_links if a in ids and b in ids)
        lineage_consistency = valid_links / len(lineage_links)

        if len(diagnoses) >= 2:
            model_agreement = SequenceMatcher(
                None,
                diagnoses[0].root_cause.lower(),
                diagnoses[1].root_cause.lower(),
            ).ratio()
        elif diagnoses:
            model_agreement = 0.65
        else:
            model_agreement = 0.0

        final = (
            0.35 * evidence_coverage
            + 0.25 * temporal_consistency
            + 0.20 * lineage_consistency
            + 0.20 * model_agreement
        )
        return ConfidenceBreakdown(
            evidence_coverage=round(evidence_coverage, 3),
            temporal_consistency=round(temporal_consistency, 3),
            lineage_consistency=round(lineage_consistency, 3),
            model_agreement=round(model_agreement, 3),
            final=round(final, 3),
        )
