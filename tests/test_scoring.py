import pytest
from app.services.demo import build_demo_incident
from app.providers.mock import MockGeminiProvider, MockLlamaProvider
from app.services.scoring import ConfidenceScorer


@pytest.mark.asyncio
async def test_confidence_is_deterministic_and_high_for_demo():
    incident = build_demo_incident()
    findings = []
    diagnoses = [
        await MockGeminiProvider().diagnose(incident, findings),
        await MockLlamaProvider().diagnose(incident, findings),
    ]
    score = ConfidenceScorer().score(incident, diagnoses)
    assert 0.75 <= score.final <= 1.0
    assert score.evidence_coverage == 1.0
