"""
JS/TS Parser — regex-based signal extraction from JavaScript/TypeScript files.

Design rationale & documented trade-off:
  A full JS/TS AST (e.g., via Babel or ts-morph) would give higher precision
  but requires a Node.js subprocess or a third-party Python binding.
  For v1 scope, regex-based parsing is chosen for:
    - Zero external dependencies beyond the Python stdlib
    - Sufficient precision for the most common signal patterns (ES import/require,
      string literals, env var references)

  Known limitations documented here:
    - Template literals (`model = \`${MODEL}\``) may not be resolved
    - Dynamic requires (require(someVar)) are not detected
    - Multi-line import splits may partially fail
    - TypeScript type annotations with model names may produce false positives

  These trade-offs are documented in README.md under "Design Decisions".
"""

import re
from pathlib import Path

from app.scanner.parsers.python_parser import RawSignal
from app.scanner.known_signals import (
    AI_LIBRARIES,
    MODEL_NAME_PATTERNS,
    ENV_KEY_PATTERNS,
    PROVIDER_ENDPOINTS,
)

# Match: import X from 'pkg'  |  import { X } from "pkg"
_ES_IMPORT_RE = re.compile(
    r"""^import\s+(?:.*?\s+from\s+)?['"](@?[\w/\-\.]+)['"]""",
    re.MULTILINE,
)
# Match: require('pkg')  |  require("pkg")
_CJS_REQUIRE_RE = re.compile(
    r"""require\s*\(\s*['"](@?[\w/\-\.]+)['"]\s*\)""",
)
# Match: import('pkg')
_DYNAMIC_IMPORT_RE = re.compile(
    r"""import\s*\(\s*['"](@?[\w/\-\.]+)['"]\s*\)""",
)
# Detect commented lines
_COMMENT_RE = re.compile(r"^\s*(?://|/\*|\*)")


def _extract_root_package(import_path: str) -> str:
    """
    Normalise a JS import path to a root package name.
    e.g. '@langchain/openai' → '@langchain/openai' (scoped — kept as-is)
          'openai/streaming' → 'openai'
    """
    if import_path.startswith("@"):
        # Scoped package: keep @scope/pkg, drop deeper paths
        parts = import_path.split("/")
        return "/".join(parts[:2])
    return import_path.split("/")[0]


class JsParser:
    """Regex-based parser for JavaScript and TypeScript files."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def parse(self) -> list[RawSignal]:
        try:
            source = self.file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []

        lines = source.splitlines()
        signals: list[RawSignal] = []

        signals.extend(self._extract_imports(source, lines))
        signals.extend(self._scan_lines(lines))
        return signals

    def _extract_imports(self, source: str, lines: list[str]) -> list[RawSignal]:
        signals: list[RawSignal] = []
        patterns = [_ES_IMPORT_RE, _CJS_REQUIRE_RE, _DYNAMIC_IMPORT_RE]

        for pattern in patterns:
            for m in pattern.finditer(source):
                pkg = _extract_root_package(m.group(1))
                if pkg in AI_LIBRARIES or pkg.replace("-", "_") in AI_LIBRARIES:
                    lineno = source[: m.start()].count("\n") + 1
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="LIBRARY_IMPORT",
                        matched_value=pkg,
                        snippet=self._snippet(lines, lineno),
                        confidence_weight=0.9,  # Slightly below Python AST
                    ))
        return signals

    def _scan_lines(self, lines: list[str]) -> list[RawSignal]:
        signals: list[RawSignal] = []
        for lineno, line in enumerate(lines, start=1):
            # Skip commented lines
            if _COMMENT_RE.match(line):
                continue

            stripped = line.strip()

            # Model name strings
            for pattern in MODEL_NAME_PATTERNS:
                m = pattern.search(stripped)
                if m:
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="MODEL_NAME_STRING",
                        matched_value=m.group(0),
                        snippet=self._snippet(lines, lineno),
                        confidence_weight=0.85,
                    ))
                    break  # One signal per line

            # Provider endpoint URLs
            for endpoint, provider in PROVIDER_ENDPOINTS.items():
                if endpoint in stripped:
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="API_ENDPOINT",
                        matched_value=endpoint,
                        snippet=self._snippet(lines, lineno),
                        confidence_weight=0.85,
                    ))
                    break

            # Env var key patterns (e.g. process.env.OPENAI_API_KEY)
            for pattern in ENV_KEY_PATTERNS:
                m = pattern.search(stripped)
                if m:
                    signals.append(RawSignal(
                        file_path=str(self.file_path),
                        line_number=lineno,
                        signal_type="ENV_VAR_KEY",
                        matched_value=m.group(0),
                        snippet=self._snippet(lines, lineno),
                        confidence_weight=0.55,
                    ))
                    break

        return signals

    def _snippet(self, lines: list[str], lineno: int, context: int = 1) -> str:
        start = max(0, lineno - 1 - context)
        end = min(len(lines), lineno + context)
        return "\n".join(lines[start:end])


def parse_js_file(file_path: Path) -> list[RawSignal]:
    """Public entry point — parse a JS/TS file and return its signals."""
    return JsParser(file_path).parse()
