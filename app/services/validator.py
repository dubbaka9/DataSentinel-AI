from app.models.domain import Incident


class ValidationService:
    def validate(self, incident: Incident) -> dict:
        # MVP deterministic checks. Replace with dbt/Soda/Great Expectations in Phase 2.
        checks = {
            "schema_contract": True,
            "null_rate": True,
            "row_count_delta_within_threshold": True,
            "downstream_model_health": True,
        }
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "rollback_required": not all(checks.values()),
        }
