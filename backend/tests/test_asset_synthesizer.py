"""
Tests for the Asset Synthesizer — validates Discovered/Inferred status logic
and asset field population.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scanner.evidence_extractor import Evidence
from app.scanner.evidence_aggregator import CandidateApp
from app.scanner.asset_synthesizer import synthesize_assets, AIAssetRecord


def _make_evidence(signal_type: str, matched_value: str, file_path: str = "app/service.py") -> Evidence:
    return Evidence(
        file_path=file_path,
        line_number=10,
        signal_type=signal_type,
        matched_value=matched_value,
        snippet=f"# example: {matched_value}",
        confidence_weight=1.0,
    )


def _make_candidate(app_name: str, evidence: list[Evidence]) -> CandidateApp:
    return CandidateApp(
        app_dir=Path(f"/fake/{app_name}"),
        app_name=app_name,
        evidence=evidence,
    )


class TestDiscoveredStatus:
    """Assets with LIBRARY_IMPORT + MODEL_NAME_STRING → status=Discovered."""

    def test_import_and_model_name_is_discovered(self):
        candidate = _make_candidate("support-portal", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
            _make_evidence("MODEL_NAME_STRING", "gpt-4o-mini"),
        ])
        assets = synthesize_assets([candidate])
        assert len(assets) == 1
        assert assets[0].status == "Discovered"

    def test_discovered_has_high_confidence(self):
        candidate = _make_candidate("my-app", [
            _make_evidence("LIBRARY_IMPORT", "anthropic"),
            _make_evidence("MODEL_NAME_STRING", "claude-3-5-sonnet-20241022"),
            _make_evidence("ENV_VAR_KEY", "ANTHROPIC_API_KEY"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].confidence_score >= 0.7

    def test_sentence_transformers_is_discovered(self):
        candidate = _make_candidate("doc-search", [
            _make_evidence("LIBRARY_IMPORT", "sentence_transformers"),
            _make_evidence("MODEL_NAME_STRING", "all-MiniLM-L6-v2"),
            _make_evidence("ENV_VAR_KEY", "HF_TOKEN"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].status == "Discovered"
        assert assets[0].provider == "Hugging Face"


class TestInferredStatus:
    """Assets with incomplete evidence → status=Inferred."""

    def test_import_only_is_inferred(self):
        candidate = _make_candidate("mystery-app", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].status == "Inferred"

    def test_manifest_only_is_inferred(self):
        candidate = _make_candidate("dep-only-app", [
            _make_evidence("MANIFEST_DEPENDENCY", "openai"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].status == "Inferred"

    def test_env_key_only_is_inferred(self):
        candidate = _make_candidate("env-only-app", [
            _make_evidence("ENV_VAR_KEY", "OPENAI_API_KEY"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].status == "Inferred"

    def test_inferred_confidence_lower_than_discovered(self):
        inferred_candidate = _make_candidate("app-a", [
            _make_evidence("ENV_VAR_KEY", "OPENAI_API_KEY"),
        ])
        discovered_candidate = _make_candidate("app-b", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
            _make_evidence("MODEL_NAME_STRING", "gpt-4o-mini"),
        ])
        assets = synthesize_assets([inferred_candidate, discovered_candidate])
        inferred = next(a for a in assets if a.application == "app-a")
        discovered = next(a for a in assets if a.application == "app-b")
        assert inferred.confidence_score < discovered.confidence_score


class TestProviderResolution:
    def test_openai_provider(self):
        candidate = _make_candidate("app", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
            _make_evidence("MODEL_NAME_STRING", "gpt-4o-mini"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].provider == "OpenAI"

    def test_hugging_face_provider(self):
        candidate = _make_candidate("app", [
            _make_evidence("LIBRARY_IMPORT", "sentence_transformers"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].provider == "Hugging Face"

    def test_provider_inferred_from_env_key_only(self):
        candidate = _make_candidate("app", [
            _make_evidence("ENV_VAR_KEY", "ANTHROPIC_API_KEY"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].provider == "Anthropic"


class TestModelResolution:
    def test_model_populated_when_present(self):
        candidate = _make_candidate("app", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
            _make_evidence("MODEL_NAME_STRING", "gpt-4o-mini"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].llm_or_model == "gpt-4o-mini"

    def test_model_none_when_not_found(self):
        candidate = _make_candidate("app", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
        ])
        assets = synthesize_assets([candidate])
        assert assets[0].llm_or_model is None


class TestMultipleApps:
    def test_two_apps_produce_two_assets(self):
        c1 = _make_candidate("support-portal", [
            _make_evidence("LIBRARY_IMPORT", "openai"),
            _make_evidence("MODEL_NAME_STRING", "gpt-4o-mini"),
        ])
        c2 = _make_candidate("doc-search", [
            _make_evidence("LIBRARY_IMPORT", "sentence_transformers"),
            _make_evidence("MODEL_NAME_STRING", "all-MiniLM-L6-v2"),
        ])
        assets = synthesize_assets([c1, c2])
        assert len(assets) == 2
        app_names = {a.application for a in assets}
        assert "support-portal" in app_names
        assert "doc-search" in app_names


class TestFullPipelineAgainstTestbed:
    """Integration test — run the complete scanner against the testbed."""

    def test_full_scan_produces_assets(self):
        testbed = Path(__file__).parent.parent.parent / "testbed"
        if not testbed.exists():
            pytest.skip("Testbed directory not found")

        from app.scanner import run_scan
        assets, evidence = run_scan(str(testbed))

        assert len(assets) >= 2, f"Expected at least 2 assets, got {len(assets)}"
        assert len(evidence) > 0

    def test_support_portal_is_discovered(self):
        testbed = Path(__file__).parent.parent.parent / "testbed"
        if not testbed.exists():
            pytest.skip("Testbed directory not found")

        from app.scanner import run_scan
        assets, _ = run_scan(str(testbed))

        portal_assets = [a for a in assets if "support" in a.application.lower()]
        assert portal_assets, "Expected support-portal asset"
        # support-portal has import + model name → Discovered
        assert portal_assets[0].status == "Discovered"

    def test_doc_search_is_discovered(self):
        testbed = Path(__file__).parent.parent.parent / "testbed"
        if not testbed.exists():
            pytest.skip("Testbed directory not found")

        from app.scanner import run_scan
        assets, _ = run_scan(str(testbed))

        search_assets = [a for a in assets if "doc" in a.application.lower() or "search" in a.application.lower()]
        assert search_assets, "Expected doc-search asset"
        assert search_assets[0].status == "Discovered"
