"""
Scanner package — public entry point.

Usage:
    from app.scanner import run_scan

    assets = run_scan("/path/to/repo")
"""

from app.scanner.evidence_extractor import extract_evidence
from app.scanner.evidence_aggregator import aggregate_evidence
from app.scanner.asset_synthesizer import synthesize_assets, AIAssetRecord
from app.scanner.evidence_extractor import Evidence


def run_scan(repo_path: str, discovery_source: str = "local") -> tuple[list[AIAssetRecord], list[Evidence]]:
    """
    Full discovery pipeline:
      repo_path → extract_evidence → aggregate_evidence → synthesize_assets

    Returns:
        Tuple of (assets, all_evidence)
        all_evidence is the flat list before grouping, for debugging.
    """
    all_evidence = extract_evidence(repo_path)
    candidates = aggregate_evidence(repo_path, all_evidence)
    assets = synthesize_assets(candidates, discovery_source=discovery_source)
    return assets, all_evidence
