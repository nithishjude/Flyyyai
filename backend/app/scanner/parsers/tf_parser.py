"""
Terraform Parser — Regex-based signal extraction from Terraform (.tf) files.

Design rationale:
  Terraform HCL is a custom syntax. Rather than pulling in a full HCL parser
  (which would add a non-trivial external dependency), we use targeted regex
  patterns against known cloud AI resource types.

  This is the same documented trade-off used for JS/TS files: regex is fast,
  has zero extra dependencies, and is precise enough for the well-known
  resource type strings that cloud AI services emit.

  Trade-off: Dynamically computed resource names or complex HCL expressions
  will not be resolved; the asset becomes 'Inferred'. This is documented as
  a known limitation.

Signal types emitted:
  - LIBRARY_IMPORT  (re-used semantically for "cloud resource declaration")
  - MODEL_NAME_STRING
  - ENV_VAR_KEY
"""

import re
from pathlib import Path
from app.scanner.parsers.python_parser import RawSignal

# ---------------------------------------------------------------------------
# Cloud AI resource type patterns → (provider, purpose_hint)
# ---------------------------------------------------------------------------
_CLOUD_AI_RESOURCES: list[tuple[re.Pattern, str, str]] = [
    # Azure OpenAI / Cognitive Services
    (
        re.compile(r'azurerm_cognitive_account', re.IGNORECASE),
        "Azure OpenAI",
        "Azure Cognitive Services / OpenAI resource declaration",
    ),
    (
        re.compile(r'azurerm_cognitive_deployment', re.IGNORECASE),
        "Azure OpenAI",
        "Azure OpenAI model deployment",
    ),
    # AWS Bedrock
    (
        re.compile(r'aws_bedrock_model', re.IGNORECASE),
        "AWS Bedrock",
        "AWS Bedrock model resource declaration",
    ),
    (
        re.compile(r'aws_sagemaker_endpoint', re.IGNORECASE),
        "AWS SageMaker",
        "AWS SageMaker inference endpoint",
    ),
    (
        re.compile(r'aws_sagemaker_model', re.IGNORECASE),
        "AWS SageMaker",
        "AWS SageMaker model resource",
    ),
    # Google Cloud AI
    (
        re.compile(r'google_vertex_ai', re.IGNORECASE),
        "Google Vertex AI",
        "Google Vertex AI resource declaration",
    ),
    (
        re.compile(r'google_ml_engine', re.IGNORECASE),
        "Google Cloud AI",
        "Google ML Engine resource",
    ),
]

# ---------------------------------------------------------------------------
# Model name strings inside .tf files
# ---------------------------------------------------------------------------
_TF_MODEL_PATTERNS: list[re.Pattern] = [
    re.compile(r'"(gpt-4[o\-]?[\w\-.]*)"', re.IGNORECASE),
    re.compile(r'"(gpt-3\.5[\w\-.]*)"', re.IGNORECASE),
    re.compile(r'"(claude-[\w\-.]+)"', re.IGNORECASE),
    re.compile(r'"(gemini-[\w\-.]+)"', re.IGNORECASE),
    re.compile(r'"(amazon\.titan[\w\-.]*)"', re.IGNORECASE),
    re.compile(r'"(anthropic\.claude[\w\-.]*)"', re.IGNORECASE),
    re.compile(r'"(meta\.llama[\w\-.]*)"', re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# API key / secret env references inside .tf files
# ---------------------------------------------------------------------------
_TF_ENV_PATTERNS: list[re.Pattern] = [
    re.compile(r'\bOPENAI_API_KEY\b'),
    re.compile(r'\bAZURE_OPENAI_API_KEY\b'),
    re.compile(r'\bAZURE_OPENAI_KEY\b'),
    re.compile(r'\bANTHROPIC_API_KEY\b'),
    re.compile(r'\bGOOGLE_API_KEY\b'),
    re.compile(r'\bGEMINI_API_KEY\b'),
    re.compile(r'\bBEDROCK_API_KEY\b'),
]


def parse_tf_file(file_path: Path) -> list[RawSignal]:
    """
    Parse a Terraform .tf file using regex and return RawSignal records.

    Detects:
      - Cloud AI resource type declarations → LIBRARY_IMPORT signal
      - Model name string literals → MODEL_NAME_STRING signal
      - AI API key / secret env variable references → ENV_VAR_KEY signal
    """
    signals: list[RawSignal] = []

    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return signals

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # ---- Cloud AI resource declarations ----
        for pattern, provider, purpose_hint in _CLOUD_AI_RESOURCES:
            m = pattern.search(stripped)
            if m:
                signals.append(RawSignal(
                    file_path=str(file_path),
                    line_number=lineno,
                    signal_type="LIBRARY_IMPORT",
                    matched_value=f"{m.group(0)} ({provider})",
                    snippet=stripped[:120],
                    confidence_weight=0.85,
                ))
                break  # one signal per line for resource type

        # ---- Model name strings ----
        for pattern in _TF_MODEL_PATTERNS:
            m = pattern.search(stripped)
            if m:
                signals.append(RawSignal(
                    file_path=str(file_path),
                    line_number=lineno,
                    signal_type="MODEL_NAME_STRING",
                    matched_value=m.group(1),
                    snippet=stripped[:120],
                    confidence_weight=0.9,
                ))
                break

        # ---- API key / secret env references ----
        for pattern in _TF_ENV_PATTERNS:
            m = pattern.search(stripped)
            if m:
                signals.append(RawSignal(
                    file_path=str(file_path),
                    line_number=lineno,
                    signal_type="ENV_VAR_KEY",
                    matched_value=m.group(0),
                    snippet=stripped[:120],
                    confidence_weight=0.55,
                ))
                break

    return signals
