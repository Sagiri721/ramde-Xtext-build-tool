from __future__ import annotations

import os
from pathlib import Path

DOCS_DIR_NAME = "01_documentation"
METAMODELS_DIR_NAME = "02_metamodels"
MODELS_DIR_NAME = "03_models"
TOOLS_DIR_NAME = "tools"

#: Environment overrides.
ENV_HOME = "CORE_HOME"  # project root
ENV_MODEL_ROOT = "USECASE_MODEL_ROOT"  # where cross-file references are searched


def project_root() -> Path:
    env = os.environ.get(ENV_HOME)
    if env:
        return Path(env).resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / METAMODELS_DIR_NAME).is_dir():
            return candidate
    raise RuntimeError(
        f"Cannot locate the project root (no '{METAMODELS_DIR_NAME}' folder above "
        f"{__file__}). Install with 'pip install -e .' or set {ENV_HOME}."
    )


def metamodels_dir() -> Path:
    return project_root() / METAMODELS_DIR_NAME


def models_dir() -> Path:
    return project_root() / MODELS_DIR_NAME


def tools_dir() -> Path:
    return project_root() / TOOLS_DIR_NAME


def generated_dir() -> Path:
    """Default output folder for generated diagrams (git-ignored)."""
    return project_root() / DOCS_DIR_NAME / "generated"


def workspace_files(model_file: str | os.PathLike | None, pattern: str) -> list[Path]:
    """Files matching ``pattern`` (e.g. ``"*.projdsl"``) that ``model_file`` may refer to.

    This plays the role of the Eclipse workspace / Xtext global index:

    * ``$USECASE_MODEL_ROOT`` if set, else the closest ancestor folder named
      ``03_models`` -> searched **recursively**;
    * otherwise only the folder of the model file itself (or the CWD for models
      parsed from a string) -> **not** recursive, so a stray model in e.g. a home
      directory never triggers a crawl of the whole disk.
    """
    env = os.environ.get(ENV_MODEL_ROOT)
    if env:
        return sorted(Path(env).resolve().rglob(pattern))
    if not model_file:
        return sorted(Path.cwd().glob(pattern))
    start = Path(model_file).resolve().parent
    for candidate in (start, *start.parents):
        if candidate.name == MODELS_DIR_NAME:
            return sorted(candidate.rglob(pattern))
    return sorted(start.glob(pattern))
