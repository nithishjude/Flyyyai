"""
Evidence Aggregator — groups raw evidence records by application boundary.

An "application boundary" is detected by the presence of a manifest file
(requirements.txt, package.json, pyproject.toml) in a directory. Evidence
found within that directory tree belongs to that application.

Pipeline position:
  Evidence Extractor → [Evidence Aggregator] → Asset Synthesizer
"""

from dataclasses import dataclass, field
from pathlib import Path

from app.scanner.evidence_extractor import Evidence
from app.scanner.file_walker import find_app_roots


@dataclass
class CandidateApp:
    """
    A candidate application boundary with all its associated evidence.
    One CandidateApp typically becomes one AIAsset record.
    """
    app_dir: Path
    app_name: str               # Derived from directory name
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def has_library_import(self) -> bool:
        return any(e.signal_type == "LIBRARY_IMPORT" for e in self.evidence)

    @property
    def has_model_name(self) -> bool:
        return any(e.signal_type == "MODEL_NAME_STRING" for e in self.evidence)

    @property
    def has_env_key(self) -> bool:
        return any(e.signal_type == "ENV_VAR_KEY" for e in self.evidence)

    @property
    def has_manifest_dependency(self) -> bool:
        return any(e.signal_type == "MANIFEST_DEPENDENCY" for e in self.evidence)

    @property
    def has_api_endpoint(self) -> bool:
        return any(e.signal_type == "API_ENDPOINT" for e in self.evidence)

    def get_library_imports(self) -> list[str]:
        return [e.matched_value for e in self.evidence if e.signal_type == "LIBRARY_IMPORT"]

    def get_model_names(self) -> list[str]:
        return [e.matched_value for e in self.evidence if e.signal_type == "MODEL_NAME_STRING"]

    def get_env_keys(self) -> list[str]:
        return [e.matched_value for e in self.evidence if e.signal_type == "ENV_VAR_KEY"]

    def get_manifest_deps(self) -> list[str]:
        return [e.matched_value for e in self.evidence if e.signal_type == "MANIFEST_DEPENDENCY"]


def aggregate_evidence(
    root_path: str | Path,
    all_evidence: list[Evidence],
) -> list[CandidateApp]:
    """
    Group evidence records into CandidateApp objects by application boundary.

    Algorithm:
      1. Identify app roots via manifest file presence (find_app_roots).
      2. For each piece of evidence, find which app root's subtree contains it.
      3. Group evidence accordingly.
      4. Evidence not belonging to any identified app root falls under a catch-all
         root-level CandidateApp.

    Returns a list of CandidateApp objects (each representing one detected app),
    filtered to only those with at least one AI-relevant signal.
    """
    root = Path(root_path).resolve()
    app_roots = find_app_roots(root)

    # Build mapping: app_root_path → CandidateApp
    candidates: dict[Path, CandidateApp] = {}
    for app_root in app_roots:
        name = _derive_app_name(app_root, root)
        candidates[app_root] = CandidateApp(app_dir=app_root, app_name=name)

    # Fallback bucket for evidence not inside any app root
    fallback = CandidateApp(app_dir=root, app_name=root.name or "root")

    for ev in all_evidence:
        ev_path = Path(ev.file_path).resolve()
        matched = False
        for app_root, candidate in candidates.items():
            try:
                ev_path.relative_to(app_root)
                candidate.evidence.append(ev)
                matched = True
                break
            except ValueError:
                continue
        if not matched:
            fallback.evidence.append(ev)

    result = list(candidates.values())
    if fallback.evidence:
        result.append(fallback)

    # Filter: only return candidates with at least one AI-relevant signal
    return [c for c in result if c.evidence]


def _derive_app_name(app_root: Path, repo_root: Path) -> str:
    """
    Derive a human-readable app name from the directory path.
    Prefers the immediate directory name; falls back to repo root name.
    """
    try:
        rel = app_root.relative_to(repo_root)
        parts = rel.parts
        if parts:
            return parts[-1]  # Last path component
    except ValueError:
        pass
    return app_root.name or "unknown-app"
