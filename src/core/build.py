"""Build all diagrams: parse models, write ``.puml`` and (if the jar is available) ``.svg``."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from textx import TextXError, metamodel_for_file

from .dsl import DSL_REGISTRY
from .plantuml import Links, RenderError, render_svg, to_plantuml

MODEL_PATTERNS = tuple(spec.pattern for spec in DSL_REGISTRY.values())


@dataclass
class Result:
    source: Path
    puml: Path | None = None
    svg: Path | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def load_model(path: str | Path):
    """Parse a model with whichever registered language matches its extension."""
    return metamodel_for_file(str(path)).model_from_file(str(path))


def discover(inputs: Iterable[str | Path]) -> list[Path]:
    """Expand files and folders (recursively) into a sorted list of model files."""
    found: set[Path] = set()
    for item in inputs:
        item = Path(item)
        if item.is_dir():
            for pattern in MODEL_PATTERNS:
                found.update(p.resolve() for p in item.rglob(pattern))
        elif item.is_file():
            found.add(item.resolve())
        else:
            raise FileNotFoundError(item)
    return sorted(found)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def write_diagram(
    model,
    target_base: Path,
    *,
    links: str = "none",
    layout: str = "dot",
    puml: bool = True,
    svg: bool = False,
) -> tuple[Path | None, Path | None]:
    """Write ``<target_base>.puml`` and/or ``<target_base>.svg`` for one parsed model."""
    source = to_plantuml(model, Links(links), layout)
    puml_path = _write(Path(f"{target_base}.puml"), source) if puml else None
    svg_path = _write(Path(f"{target_base}.svg"), render_svg(source)) if svg else None
    return puml_path, svg_path


def build_file(
    path: Path, out_dir: Path, base_dir: Path, *, links: str, layout: str, svg: bool
) -> Result:
    """Build one model. Errors are captured in the result so one bad file doesn't stop the rest."""
    result = Result(source=path)
    try:
        try:
            rel_parent = path.parent.relative_to(base_dir)
        except ValueError:
            rel_parent = Path()
        base = out_dir / rel_parent / path.name  # e.g. smarthome.ucdsl -> smarthome.ucdsl.svg
        result.puml, result.svg = write_diagram(
            load_model(path), base, links=links, layout=layout, svg=svg
        )
    except (TextXError, RenderError, OSError, ValueError) as exc:
        result.error = str(exc)
    return result


def build_all(
    inputs: Iterable[str | Path],
    out_dir: Path,
    *,
    links: str = "vscode",
    layout: str = "dot",
    svg: bool = True,
) -> list[Result]:
    inputs = [Path(i) for i in inputs]
    files = discover(inputs)
    dirs = [i.resolve() for i in inputs if i.is_dir()]
    results = []
    for file in files:
        base_dir = next((d for d in dirs if d in file.parents), file.parent)
        results.append(build_file(file, out_dir, base_dir, links=links, layout=layout, svg=svg))
    return results


def watch(inputs: Iterable[str | Path], rebuild: Callable[[], None], *, interval: float = 1.0) -> None:
    """Poll the model files and call ``rebuild`` once at start and again after every change."""
    inputs = list(inputs)

    def snapshot() -> dict[Path, int]:
        return {f: f.stat().st_mtime_ns for f in discover(inputs) if f.exists()}

    last = snapshot()
    rebuild()
    while True:
        time.sleep(interval)
        current = snapshot()
        if current != last:
            last = current
            rebuild()
