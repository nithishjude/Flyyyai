"""
Tests for the Python AST parser.
Uses fixture source strings (no file I/O) to test signal extraction precisely.
"""

import ast
import sys
import os
from pathlib import Path
import tempfile
import textwrap

import pytest

# Add backend root to path so imports resolve correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scanner.parsers.python_parser import parse_python_file, PythonParser


def _write_temp_py(source: str) -> Path:
    """Write source to a temp .py file and return its path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
    tmp.write(textwrap.dedent(source))
    tmp.close()
    return Path(tmp.name)


class TestLibraryImportDetection:
    def test_detects_openai_import(self):
        src = "import openai\nclient = openai.OpenAI()\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        types = [s.signal_type for s in signals]
        values = [s.matched_value for s in signals]
        assert "LIBRARY_IMPORT" in types
        assert any("openai" in v for v in values)

    def test_detects_from_import(self):
        src = "from sentence_transformers import SentenceTransformer\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "LIBRARY_IMPORT" for s in signals)
        assert any("sentence_transformers" in s.matched_value for s in signals)

    def test_detects_anthropic_import(self):
        src = "import anthropic\nclient = anthropic.Anthropic()\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "LIBRARY_IMPORT" and "anthropic" in s.matched_value for s in signals)

    def test_skips_non_ai_imports(self):
        src = "import os\nimport sys\nfrom pathlib import Path\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert not any(s.signal_type == "LIBRARY_IMPORT" for s in signals)

    def test_detects_langchain_import(self):
        src = "from langchain_openai import ChatOpenAI\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "LIBRARY_IMPORT" for s in signals)


class TestModelNameDetection:
    def test_detects_gpt4o_mini(self):
        src = 'model = "gpt-4o-mini"\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "MODEL_NAME_STRING" and "gpt-4o-mini" in s.matched_value for s in signals)

    def test_detects_claude_model(self):
        src = 'MODEL = "claude-3-5-sonnet-20241022"\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "MODEL_NAME_STRING" for s in signals)

    def test_detects_miniLM(self):
        src = 'EMBEDDING_MODEL = "all-MiniLM-L6-v2"\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "MODEL_NAME_STRING" and "MiniLM" in s.matched_value for s in signals)

    def test_detects_text_embedding_model(self):
        src = 'model_id = "text-embedding-3-small"\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "MODEL_NAME_STRING" for s in signals)

    def test_no_false_positive_random_string(self):
        src = 'message = "hello world"\npath = "/api/v1/users"\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert not any(s.signal_type == "MODEL_NAME_STRING" for s in signals)


class TestEnvKeyDetection:
    def test_detects_openai_api_key_in_string(self):
        src = 'key = os.environ.get("OPENAI_API_KEY")\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "ENV_VAR_KEY" and "OPENAI_API_KEY" in s.matched_value for s in signals)

    def test_detects_hf_token(self):
        src = 'token = os.getenv("HF_TOKEN", "")\n'
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        assert any(s.signal_type == "ENV_VAR_KEY" and "HF_TOKEN" in s.matched_value for s in signals)


class TestSyntaxErrorFallback:
    def test_fallback_on_invalid_python(self):
        """Parser should not raise on files with syntax errors."""
        src = "def broken(\nprint('missing paren'\nimport openai\n"
        path = _write_temp_py(src)
        # Should not raise
        signals = parse_python_file(path)
        # May or may not find signals, but must not crash
        assert isinstance(signals, list)

    def test_fallback_detects_import_in_malformed_file(self):
        src = "import openai\ndef broken(\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        # Fallback regex should still find the import
        assert any(s.signal_type == "LIBRARY_IMPORT" for s in signals)


class TestLineNumbers:
    def test_correct_line_number_for_import(self):
        src = "# comment\nimport openai\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        import_signals = [s for s in signals if s.signal_type == "LIBRARY_IMPORT"]
        assert import_signals
        assert import_signals[0].line_number == 2

    def test_correct_line_number_for_model_name(self):
        src = "\n\nMODEL = 'gpt-4o-mini'\n"
        path = _write_temp_py(src)
        signals = parse_python_file(path)
        model_signals = [s for s in signals if s.signal_type == "MODEL_NAME_STRING"]
        assert model_signals
        assert model_signals[0].line_number == 3
