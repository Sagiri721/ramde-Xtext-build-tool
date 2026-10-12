"""textX generator entry points generated from the DSL registry.

    textx generate 04_models/smarthome.ucdsl --target plantuml
    textx generate 04_models/smarthome.ucdsl --target svg --links vscode -o out/
    textx list-generators

Without ``-o`` the output goes to ``02_documentation/generated`` (not next to the model).
For whole-project builds and watch mode use the ``ramde`` CLI instead.
"""
from __future__ import annotations

from pathlib import Path

from textx import TextXError, generator
from textx.registration import GeneratorParam

from . import paths
from .build import write_diagram
from .dsl import DSL_REGISTRY
from .plantuml import RenderError

_PARAMS = [
    GeneratorParam("links", "Node links: 'none' (default) or 'vscode' (click a node to open the source)", False),
    GeneratorParam("layout", "'dot' (default, needs Graphviz) or 'smetana' (built-in, no Graphviz)", False),
]


def _run(model, output_path, overwrite, links, layout, *, svg: bool) -> None:
    out_dir = Path(output_path) if output_path else paths.generated_dir()
    base = out_dir / Path(model._tx_filename).name
    suffix = ".svg" if svg else ".puml"
    target = Path(f"{base}{suffix}")
    if target.exists() and not overwrite:
        print(f"-- Not overwriting {target} (use --overwrite)")
        return
    try:
        write_diagram(
            model, base, links=str(links), layout=str(layout), puml=not svg, svg=svg
        )
    except (RenderError, ValueError) as exc:
        raise TextXError(str(exc)) from exc
    print(f"-- Generated {target}")


def _generator_entry_point(spec, target):
    is_svg = target == "svg"

    def generate(metamodel, model, output_path, overwrite, debug, links="none", layout="dot"):
        _run(model, output_path, overwrite, links, layout, svg=is_svg)

    generate.__doc__ = f"Generate {target} output for {spec.description}"
    return generator(spec.name, target, custom_args=_PARAMS)(generate)


for _spec in DSL_REGISTRY.values():
    for _target in ("plantuml", "svg"):
        globals()[f"{_spec.name}_{_target}"] = _generator_entry_point(_spec, _target)
