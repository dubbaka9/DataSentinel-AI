from datetime import datetime, timedelta, timezone
from uuid import uuid4
from app.models.domain import Evidence, Incident, Severity


def build_demo_incident() -> Incident:
    base = datetime.now(timezone.utc) - timedelta(minutes=20)
    return Incident(
        id=f"inc-{uuid4().hex[:8]}",
        title="Customer dimension pipeline failure after upstream schema change",
        severity=Severity.high,
        pipeline="customer_360_daily",
        asset="analytics.dim_customer",
        symptoms=[
            "Spark AnalysisException: unresolved column customer_id",
            "dbt customer model failed",
            "data-quality freshness SLA breached",
        ],
        metadata={
            "downstream_assets": 8,
            "changes_transformation_logic": True,
            "sensitive_data": False,
            "data_loss_possible": False,
            "rollback_available": True,
        },
        evidence=[
            Evidence(
                id="deployment_event",
                kind="deployment",
                source="deployments-service",
                timestamp=base,
                summary="Upstream customer-api deployment completed",
                details={"version": "2026.09.28.4"},
            ),
            Evidence(
                id="schema_change",
                kind="schema",
                source="schema-registry",
                timestamp=base + timedelta(seconds=13),
                summary="Field customer_id renamed to customer_key",
                details={"removed": ["customer_id"], "added": ["customer_key"]},
            ),
            Evidence(
                id="spark_failure",
                kind="pipeline",
                source="spark-driver",
                timestamp=base + timedelta(minutes=3, seconds=38),
                summary="Spark job failed: customer_id cannot be resolved",
                details={"job": "normalize_customer"},
            ),
            Evidence(
                id="dbt_failure",
                kind="downstream",
                source="dbt-run-results",
                timestamp=base + timedelta(minutes=4, seconds=7),
                summary="dim_customer model failed because customer_id was absent",
                details={"model": "dim_customer"},
            ),
            Evidence(
                id="quality_alert",
                kind="quality",
                source="quality-monitor",
                timestamp=base + timedelta(minutes=4, seconds=12),
                summary="Freshness and required-column checks failed",
                details={"checks": ["freshness", "required_column:customer_id"]},
            ),
        ],
    )
