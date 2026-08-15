"""
File Walker — traverses a local repository directory and yields scannable files.

Design decisions:
  - Operates on local paths only in v1 (GitHub repos should be cloned externally
    or passed as local paths after cloning).
  - Skips well-known non-source directories to avoid scanning vendored dependencies.
  - Returns a generator to keep memory usage flat for large repos.
"""

import os
from pathlib import Path
from typing import Generator, Tuple

# Directories to skip entirely (will not descend into these).
# NOTE: ".env" is intentionally NOT in this set — a directory literally named
# ".env" would also match the walk_repo dot-prefix guard below.  We keep .env
# files reachable via MANIFEST_FILES so the extractor can read them.
SKIP_DIRS: frozenset[str] = frozenset({
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "site-packages",
    "eggs",
    ".eggs",
    "target",          # Rust/Java build output
    "vendor",          # Go/Ruby vendoring
    ".terraform",
    ".serverless",
})

# File extensions we can parse
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".mjs",
    ".cjs",
})

# Manifest files we handle specially
MANIFEST_FILES: frozenset[str] = frozenset({
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "package.json",
    # Lock files are intentionally excluded: we don't parse them and including
    # them here added dead code paths in the extractor.
    ".env",
    ".env.example",
    ".env.local",
    ".env.production",
    ".env.development",
})

LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}


def walk_repo(
    root_path: str | Path,
) -> Generator[Tuple[Path, str, str], None, None]:
    """
    Walk a repository directory and yield (file_path, language, file_category) tuples.

    file_category is one of:
      "source"   — a parseable source file (.py, .js, .ts, etc.)
      "manifest" — a dependency/config file (requirements.txt, package.json, .env*)
    """
    root = Path(root_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Prune skip directories in-place so os.walk doesn't descend into them
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]

        for filename in filenames:
            file_path = Path(dirpath) / filename
            ext = file_path.suffix.lower()

            if filename in MANIFEST_FILES:
                lang = "manifest"
                if filename.startswith(".env"):
                    lang = "dotenv"
                yield file_path, lang, "manifest"
                continue

            if ext in SUPPORTED_EXTENSIONS:
                lang = LANGUAGE_MAP.get(ext, "unknown")
                yield file_path, lang, "source"


def find_app_roots(root_path: str | Path) -> list[Path]:
    """
    Identify application roots within a repo by locating manifest files
    (requirements.txt, package.json) that indicate a self-contained app.

    Returns a list of directory paths, each representing one application.
    """
    root = Path(root_path).resolve()
    app_roots: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]

        current = Path(dirpath)
        if any(f in filenames for f in ("requirements.txt", "package.json", "pyproject.toml")):
            app_roots.append(current)
            # Don't descend further — nested manifests are considered separate apps
            dirnames[:] = []

    # If no app roots found, treat the whole repo as one app
    if not app_roots:
        app_roots = [root]

    return app_roots
