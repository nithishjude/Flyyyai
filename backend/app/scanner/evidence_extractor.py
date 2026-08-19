"""
Evidence Extractor — orchestrates parsers across all files in a repo and
produces a flat list of raw Evidence records.

Pipeline position:
  File walker → [Evidence Extractor] → Evidence Aggregator → Asset Synthesizer
"""

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.scanner.file_walker import walk_repo
from app.scanner.parsers.python_parser import parse_python_file, RawSignal
from app.scanner.parsers.js_parser import parse_js_file
from app.scanner.parsers.tf_parser import parse_tf_file
from app.scanner.known_signals import (
    AI_LIBRARIES,
    MODEL_NAME_PATTERNS,
    ENV_KEY_PATTERNS,
    MANIFEST_AI_PACKAGES,
)


@dataclass
class Evidence:
    """
    A single raw evidence record — the atomic unit of discovery.
    These are stored directly in the DB and linked to assets.
    """
    file_path: str
    line_number: int
    signal_type: str        # LIBRARY_IMPORT | MODEL_NAME_STRING | ENV_VAR_KEY | API_ENDPOINT | MANIFEST_DEPENDENCY
    matched_value: str
    snippet: str
    confidence_weight: float = 1.0


def _signal_to_evidence(sig: RawSignal) -> Evidence:
    return Evidence(
        file_path=sig.file_path,
        line_number=sig.line_number,
        signal_type=sig.signal_type,
        matched_value=sig.matched_value,
        snippet=sig.snippet,
        confidence_weight=sig.confidence_weight,
    )


# ---------------------------------------------------------------------------
# Manifest parsers
# ---------------------------------------------------------------------------

def _parse_requirements_txt(file_path: Path) -> list[Evidence]:
    """Extract AI package dependencies from requirements.txt."""
    evidence: list[Evidence] = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return evidence

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Strip version specifiers: openai>=1.0 → openai
        pkg_name = re.split(r"[>=<!;@ ]", stripped)[0].lower().strip()
        if pkg_name in MANIFEST_AI_PACKAGES:
            evidence.append(Evidence(
                file_path=str(file_path),
                line_number=lineno,
                signal_type="MANIFEST_DEPENDENCY",
                matched_value=pkg_name,
                snippet=stripped,
                confidence_weight=0.7,
            ))
    return evidence


def _parse_package_json(file_path: Path) -> list[Evidence]:
    """Extract AI npm package dependencies from package.json.

    Line numbers are resolved by scanning the raw JSON text line-by-line so
    that evidence records point to the exact line in the manifest file, making
    the traceability chain accurate.
    """
    import json
    evidence: list[Evidence] = []
    try:
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw_text)
    except (OSError, json.JSONDecodeError):
        return evidence

    # Build a line-number index: package_name → first line it appears on
    raw_lines = raw_text.splitlines()
    lineno_map: dict[str, int] = {}
    for i, line in enumerate(raw_lines, start=1):
        stripped = line.strip().strip('"')
        # Match "package-name": "version" patterns
        if ":" in stripped:
            pkg = stripped.split(":")[0].strip().strip('"')
            if pkg and pkg not in lineno_map:
                lineno_map[pkg] = i

    dep_sections = ["dependencies", "devDependencies", "peerDependencies"]
    for section in dep_sections:
        for pkg_name in data.get(section, {}).keys():
            if pkg_name.lower() in MANIFEST_AI_PACKAGES or pkg_name in MANIFEST_AI_PACKAGES:
                line = lineno_map.get(pkg_name, 0)
                evidence.append(Evidence(
                    file_path=str(file_path),
                    line_number=line,
                    signal_type="MANIFEST_DEPENDENCY",
                    matched_value=pkg_name,
                    snippet=f'"{pkg_name}": "{data[section][pkg_name]}"',
                    confidence_weight=0.7,
                ))
    return evidence


def _parse_dotenv(file_path: Path) -> list[Evidence]:
    """Extract AI-related env var keys from .env / .env.example files."""
    evidence: list[Evidence] = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return evidence

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for pattern in ENV_KEY_PATTERNS:
            m = pattern.search(stripped)
            if m:
                evidence.append(Evidence(
                    file_path=str(file_path),
                    line_number=lineno,
                    signal_type="ENV_VAR_KEY",
                    matched_value=m.group(0),
                    snippet=stripped,
                    confidence_weight=0.55,
                ))
                break
    return evidence


def _parse_pyproject_toml(file_path: Path) -> list[Evidence]:
    """Extract AI deps from pyproject.toml [tool.poetry.dependencies] etc."""
    evidence: list[Evidence] = []
    try:
        data = tomllib.loads(file_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return evidence

    # Walk any nested dict looking for known AI package names as keys
    def _scan_dict(d: dict) -> None:
        for k, v in d.items():
            pkg = k.lower()
            if pkg in MANIFEST_AI_PACKAGES:
                evidence.append(Evidence(
                    file_path=str(file_path),
                    line_number=0,
                    signal_type="MANIFEST_DEPENDENCY",
                    matched_value=k,
                    snippet=f"{k} = {v!r}",
                    confidence_weight=0.7,
                ))
            if isinstance(v, dict):
                _scan_dict(v)

    _scan_dict(data)
    return evidence


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_evidence(root_path: str | Path) -> list[Evidence]:
    """
    Walk the repository at root_path and extract all raw evidence records.

    Returns a flat list of Evidence objects covering:
      - Source code signals (LIBRARY_IMPORT, MODEL_NAME_STRING, ENV_VAR_KEY, API_ENDPOINT)
      - Manifest signals (MANIFEST_DEPENDENCY, ENV_VAR_KEY from .env files)
    """
    all_evidence: list[Evidence] = []

    for file_path, lang, category in walk_repo(root_path):
        if category == "source":
            if lang == "python":
                signals = parse_python_file(file_path)
            elif lang in ("javascript", "typescript"):
                signals = parse_js_file(file_path)
            elif lang == "terraform":
                signals = parse_tf_file(file_path)
            else:
                signals = []

            all_evidence.extend(_signal_to_evidence(s) for s in signals)

        elif category == "manifest":
            name = file_path.name.lower()
            if name == "requirements.txt":
                all_evidence.extend(_parse_requirements_txt(file_path))
            elif name == "package.json":
                all_evidence.extend(_parse_package_json(file_path))
            elif name.startswith(".env"):
                all_evidence.extend(_parse_dotenv(file_path))
            elif name == "pyproject.toml":
                all_evidence.extend(_parse_pyproject_toml(file_path))

    return all_evidence
