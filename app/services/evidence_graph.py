from __future__ import annotations

import networkx as nx
from app.models.domain import Evidence, Incident


class EvidenceGraph:
    """Builds a causality-oriented graph from structured incident evidence."""

    def build(self, incident: Incident) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_node("incident", kind="incident", label=incident.title)

        ordered = sorted(incident.evidence, key=lambda e: e.timestamp)
        previous: Evidence | None = None
        for item in ordered:
            graph.add_node(
                item.id,
                kind=item.kind,
                label=item.summary,
                source=item.source,
                timestamp=item.timestamp.isoformat(),
                reliability=item.reliability,
            )
            graph.add_edge(item.id, "incident", relation="supports")
            if previous:
                graph.add_edge(previous.id, item.id, relation="precedes")
            previous = item

        # Domain-specific causal links when evidence ids are present.
        ids = {e.id for e in incident.evidence}
        for src, dst, relation in [
            ("deployment_event", "schema_change", "introduced"),
            ("schema_change", "spark_failure", "caused"),
            ("spark_failure", "dbt_failure", "propagated"),
            ("dbt_failure", "quality_alert", "triggered"),
        ]:
            if src in ids and dst in ids:
                graph.add_edge(src, dst, relation=relation)
        return graph

    def summarize(self, graph: nx.DiGraph) -> dict:
        return {
            "nodes": [dict(id=n, **attrs) for n, attrs in graph.nodes(data=True)],
            "edges": [dict(source=a, target=b, **attrs) for a, b, attrs in graph.edges(data=True)],
        }
