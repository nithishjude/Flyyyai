"""
Python Parser — AST-based signal extraction from Python source files.

Design rationale:
  Using Python's built-in `ast` module gives us accurate parse trees without
  external dependencies. This lets us:
    - Distinguish import statements from string literals precisely
    - Walk function bodies to co-locate imports + model-name strings
    - Avoid false positives from commented-out code (AST skips comments)

  Trade-off: AST parsing requires syntactically valid Python. Files with
  syntax errors fall back to a line-by-line regex scan so we don't lose coverage.
"""

import ast
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.scanner.known_signals import (
    AI_LIBRARIES,
    MODEL_NAME_PATTERNS,
    ENV_KEY_PATTERNS,
    PROVIDER_ENDPOINTS,
)


@dataclass
class RawSignal:
    """A single piece of AI-relevant evidence extracted from a file."""
    file_path: str
    line_number: int
    signal_type: str        # LIBRARY_IMPORT | MODEL_NAME_STRING | ENV_VAR_KEY | API_ENDPOINT
    matched_value: str      # The exact token that triggered detection
    snippet: str            # 1-3 lines of surrounding source context
    confidence_weight: float = 1.0   # 0.0–1.0; higher = more unambiguous


class PythonParser:
    """
    Parses a Python file using ast and emits RawSignal records.
    Falls back to regex on syntax errors.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._source_lines: list[str] = []

    def parse(self) -> list[RawSignal]:
        """Parse the file and return all detected signals."""
        try:
            source = self.file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []

        self._source_lines = source.splitlines()

        try:
            tree = ast.parse(source, filename=str(self.file_path))
            return self._walk_ast(tree)
        except SyntaxError:
            # Fallback: regex-based scan (lower confidence)
            return self._regex_fallback(source)

    def _walk_ast(self, tree: ast.AST) -> list[RawSignal]:
        signals: list[RawSignal] = []
        visitor = _SignalVisitor(self.file_path, self._source_lines)
        visitor.visit(tree)
        return visitor.signals

    def _regex_fallback(self, source: str) -> list[RawSignal]:
        """Regex scan for syntax-error files — lower confidence."""
        signals: list[RawSignal] = []
        for lineno, line in enumerate(self._source_lines, start=1):
            snippet = self._get_snippet(lineno)
            # Check imports
            import_match = re.match(r"^\s*(?:import|from)\s+([\w.]+)", line)
            if import_match:
                lib = import_match.group(1).split(".")[0].replace("-", "_")
                if lib in AI_LIBRARIES:
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="LIBRARY_IMPORT",
                        matched_value=lib,
                        snippet=snippet,
                        confidence_weight=0.7,  # Lower than AST
                    ))
            # Check model names
            for pattern in MODEL_NAME_PATTERNS:
                m = pattern.search(line)
                if m and not line.strip().startswith("#"):
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="MODEL_NAME_STRING",
                        matched_value=m.group(0),
                        snippet=snippet,
                        confidence_weight=0.6,
                    ))
            # Check env keys
            for pattern in ENV_KEY_PATTERNS:
                m = pattern.search(line)
                if m:
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="ENV_VAR_KEY",
                        matched_value=m.group(0),
                        snippet=snippet,
                        confidence_weight=0.5,
                    ))
        return signals

    def _get_snippet(self, lineno: int, context: int = 1) -> str:
        start = max(0, lineno - 1 - context)
        end = min(len(self._source_lines), lineno + context)
        return "\n".join(self._source_lines[start:end])


class _SignalVisitor(ast.NodeVisitor):
    """AST node visitor that collects AI-relevant signals."""

    def __init__(self, file_path: Path, source_lines: list[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.signals: list[RawSignal] = []

    # ------------------------------------------------------------------
    # Import statements
    # ------------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root_module = alias.name.split(".")[0].replace("-", "_")
            normalised = root_module.replace("-", "_")
            if normalised in AI_LIBRARIES:
                self.signals.append(RawSignal(
                    file_path=str(self.file_path),
                    line_number=node.lineno,
                    signal_type="LIBRARY_IMPORT",
                    matched_value=alias.name,
                    snippet=self._snippet(node.lineno),
                    confidence_weight=1.0,
                ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = (node.module or "").split(".")[0].replace("-", "_")
        if module in AI_LIBRARIES:
            self.signals.append(RawSignal(
                file_path=str(self.file_path),
                line_number=node.lineno,
                signal_type="LIBRARY_IMPORT",
                matched_value=node.module or module,
                snippet=self._snippet(node.lineno),
                confidence_weight=1.0,
            ))
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # String constants (model names, endpoint URLs, env var names)
    # ------------------------------------------------------------------

    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.s, str):
            self.generic_visit(node)
            return

        value = node.s
        lineno = node.lineno

        # Model name check
        for pattern in MODEL_NAME_PATTERNS:
            m = pattern.fullmatch(value) or pattern.search(value)
            if m:
                self.signals.append(RawSignal(
                    file_path=str(self.file_path),
                    line_number=lineno,
                    signal_type="MODEL_NAME_STRING",
                    matched_value=m.group(0),
                    snippet=self._snippet(lineno),
                    confidence_weight=0.9,
                ))
                break  # One signal per string constant

        # API endpoint check
        for endpoint, provider in PROVIDER_ENDPOINTS.items():
            if endpoint in value:
                self.signals.append(RawSignal(
                    file_path=str(self.file_path),
                    line_number=lineno,
                    signal_type="API_ENDPOINT",
                    matched_value=endpoint,
                    snippet=self._snippet(lineno),
                    confidence_weight=0.85,
                ))
                break

        # Env var key patterns within string (e.g., os.environ.get("OPENAI_API_KEY"))
        for pattern in ENV_KEY_PATTERNS:
            m = pattern.search(value)
            if m:
                self.signals.append(RawSignal(
                    file_path=str(self.file_path),
                    line_number=lineno,
                    signal_type="ENV_VAR_KEY",
                    matched_value=m.group(0),
                    snippet=self._snippet(lineno),
                    confidence_weight=0.6,
                ))
                break

        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _snippet(self, lineno: int, context: int = 1) -> str:
        start = max(0, lineno - 1 - context)
        end = min(len(self.source_lines), lineno + context)
        return "\n".join(self.source_lines[start:end])


def parse_python_file(file_path: Path) -> list[RawSignal]:
    """Public entry point — parse a Python file and return its signals."""
    return PythonParser(file_path).parse()
