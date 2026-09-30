from app.models.domain import AgentFinding, Incident, ModelDiagnosis
from app.providers.base import DiagnosisProvider


class MockGeminiProvider(DiagnosisProvider):
    name = "gemini-mock"

    async def diagnose(self, incident: Incident, findings: list[AgentFinding]) -> ModelDiagnosis:
        return ModelDiagnosis(
            provider=self.name,
            root_cause="An upstream schema rename removed customer_id before the Spark transformation, causing downstream dbt failure.",
            evidence_ids=["deployment_event", "schema_change", "spark_failure", "dbt_failure"],
            remediation="Restore the customer_id contract or update the transformation mapping after approval, then rerun and validate.",
        )


class MockLlamaProvider(DiagnosisProvider):
    name = "llama-mock"

    async def diagnose(self, incident: Incident, findings: list[AgentFinding]) -> ModelDiagnosis:
        return ModelDiagnosis(
            provider=self.name,
            root_cause="The customer_id field was renamed upstream, breaking the Spark input schema and propagating into the dbt model.",
            evidence_ids=["schema_change", "spark_failure", "dbt_failure"],
            remediation="Reconcile the schema mapping for customer_id, dry-run the pipeline, and validate downstream contracts.",
        )
