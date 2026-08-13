"""
Tests for the Evidence Extractor — validates end-to-end signal detection
against the testbed directory fixtures.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scanner.evidence_extractor import extract_evidence, Evidence


TESTBED_ROOT = Path(__file__).parent.parent.parent / "testbed"
SUPPORT_PORTAL = TESTBED_ROOT / "support-portal"
DOC_SEARCH = TESTBED_ROOT / "doc-search"


class TestSupportPortalExtraction:
    @pytest.fixture(scope="class")
    def evidence(self):
        if not SUPPORT_PORTAL.exists():
            pytest.skip("Testbed support-portal not found")
        return extract_evidence(SUPPORT_PORTAL)

    def test_finds_openai_library_import(self, evidence):
        imports = [e for e in evidence if e.signal_type == "LIBRARY_IMPORT"]
        assert any("openai" in e.matched_value.lower() for e in imports), \
            "Expected openai LIBRARY_IMPORT signal in support-portal"

    def test_finds_gpt_model_name(self, evidence):
        model_signals = [e for e in evidence if e.signal_type == "MODEL_NAME_STRING"]
        assert any("gpt" in e.matched_value.lower() for e in model_signals), \
            "Expected GPT MODEL_NAME_STRING signal in support-portal"

    def test_finds_openai_api_key_env_var(self, evidence):
        env_signals = [e for e in evidence if e.signal_type == "ENV_VAR_KEY"]
        assert any("OPENAI_API_KEY" in e.matched_value for e in env_signals), \
            "Expected OPENAI_API_KEY ENV_VAR_KEY signal in support-portal"

    def test_finds_manifest_dependency(self, evidence):
        manifest = [e for e in evidence if e.signal_type == "MANIFEST_DEPENDENCY"]
        assert any("openai" in e.matched_value.lower() for e in manifest), \
            "Expected openai MANIFEST_DEPENDENCY in requirements.txt"

    def test_evidence_has_valid_file_paths(self, evidence):
        for e in evidence:
            assert e.file_path, "Evidence must have a non-empty file_path"
            assert e.signal_type in {
                "LIBRARY_IMPORT", "MODEL_NAME_STRING", "ENV_VAR_KEY",
                "API_ENDPOINT", "MANIFEST_DEPENDENCY"
            }, f"Unknown signal type: {e.signal_type}"

    def test_evidence_has_snippets(self, evidence):
        for e in evidence:
            assert e.snippet, f"Evidence at {e.file_path}:{e.line_number} has empty snippet"


class TestDocSearchExtraction:
    @pytest.fixture(scope="class")
    def evidence(self):
        if not DOC_SEARCH.exists():
            pytest.skip("Testbed doc-search not found")
        return extract_evidence(DOC_SEARCH)

    def test_finds_sentence_transformers_import(self, evidence):
        imports = [e for e in evidence if e.signal_type == "LIBRARY_IMPORT"]
        assert any("sentence_transformer" in e.matched_value.lower() for e in imports), \
            "Expected sentence_transformers LIBRARY_IMPORT in doc-search"

    def test_finds_miniLM_model_name(self, evidence):
        model_signals = [e for e in evidence if e.signal_type == "MODEL_NAME_STRING"]
        assert any("MiniLM" in e.matched_value for e in model_signals), \
            "Expected all-MiniLM MODEL_NAME_STRING in doc-search"

    def test_finds_hf_token_env_var(self, evidence):
        env_signals = [e for e in evidence if e.signal_type == "ENV_VAR_KEY"]
        assert any("HF_TOKEN" in e.matched_value for e in env_signals), \
            "Expected HF_TOKEN ENV_VAR_KEY in doc-search"

    def test_finds_faiss_dependency(self, evidence):
        manifest = [e for e in evidence if e.signal_type == "MANIFEST_DEPENDENCY"]
        assert any("faiss" in e.matched_value.lower() for e in manifest), \
            "Expected faiss MANIFEST_DEPENDENCY in doc-search requirements.txt"


class TestFileWalkerExclusions:
    def test_skips_venv_directories(self, tmp_path):
        """Ensure file walker does not descend into venv directories."""
        # Create a fake venv with a Python file that looks like an AI import
        venv_dir = tmp_path / "venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "openai_wrapper.py").write_text("import openai\n")
        # Also create a real source file
        (tmp_path / "app.py").write_text("print('hello')\n")

        evidence = extract_evidence(tmp_path)
        file_paths = [e.file_path for e in evidence]
        assert not any("venv" in fp for fp in file_paths), \
            "File walker should not scan inside venv/"

    def test_skips_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules" / "@openai"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("import openai from 'openai';\n")
        (tmp_path / "main.js").write_text("console.log('hello');\n")

        evidence = extract_evidence(tmp_path)
        file_paths = [e.file_path for e in evidence]
        assert not any("node_modules" in fp for fp in file_paths)
