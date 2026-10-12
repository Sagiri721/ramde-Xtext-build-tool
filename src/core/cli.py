from __future__ import annotations

import sys
from pathlib import Path

import click
from textx import TextXError, language_descriptions

from . import __version__, build as build_mod, paths
from .dsl import DSL_REGISTRY
from .plantuml import LAYOUTS, LINK_STYLES
from .plantuml import render


def _common_options(fn):
    fn = click.option(
        "--layout", type=click.Choice(LAYOUTS), default="dot", show_default=True,
        help="'smetana' is PlantUML's built-in layout engine (no Graphviz needed).",
    )(fn)
    fn = click.option(
        "--links", type=click.Choice(LINK_STYLES), default="vscode", show_default=True,
        help="'vscode': clicking a node in the SVG opens the source line in VS Code.",
    )(fn)
    fn = click.option(
        "--svg/--no-svg", default=True, show_default=True,
        help="Also render SVG (needs tools/plantuml.jar and Java).",
    )(fn)
    fn = click.option(
        "-o", "--out", "out_dir", type=click.Path(file_okay=False, path_type=Path),
        help="Output folder [default: 02_documentation/generated].",
    )(fn)
    fn = click.argument(
        "inputs", nargs=-1, type=click.Path(exists=True, path_type=Path),
    )(fn)
    return fn


def _run_build(inputs, out_dir, svg, links, layout) -> bool:
    inputs = inputs or (paths.models_dir(),)
    out_dir = out_dir or paths.generated_dir()
    if svg and render.find_plantuml_jar() is None:
        click.echo("warning: PlantUML jar not found, writing .puml only")
        svg = False
    results = build_mod.build_all(inputs, out_dir, links=links, layout=layout, svg=svg)
    for r in results:
        if r.ok:
            click.echo(f"OK    {r.source.name:<28} -> {(r.svg or r.puml)}")
        else:
            click.echo(f"FAIL  {r.source.name}: {r.error}", err=True)
    failed = sum(not r.ok for r in results)
    click.echo(f"{len(results) - failed} built, {failed} failed.")
    return failed == 0


@click.group()
@click.version_option(__version__)
def main():
    """RAMDE DSL tooling (textX + PlantUML)."""


@main.command("build")
@_common_options
def build_cmd(inputs, out_dir, svg, links, layout):
    """Generate diagrams for INPUTS (files or folders; default: 04_models)."""
    sys.exit(0 if _run_build(inputs, out_dir, svg, links, layout) else 1)

@main.command("watch")
@_common_options
def watch_cmd(inputs, out_dir, svg, links, layout):
    """Rebuild diagrams whenever a model file changes (Ctrl-C to stop).

    Grammar changes (03_metamodels) need a restart: textX loads them once per process.
    """
    inputs = inputs or (paths.models_dir(),)

    def rebuild():
        click.echo("rebuilding...")
        _run_build(inputs, out_dir, svg, links, layout)

    click.echo(f"Watching {', '.join(str(i) for i in inputs)} ...")
    try:
        build_mod.watch(inputs, rebuild)
    except KeyboardInterrupt:
        click.echo("stopped.")

@main.command("clean")
def clean_cmd():
    """Clean up generated files"""
    out_dir = paths.generated_dir()
    if out_dir.exists():
        for f in out_dir.iterdir():
            f.unlink()
        click.echo(f"Cleaned up {out_dir}")
    else:
        click.echo(f"No generated files found in {out_dir}")


@main.command("health")
def health_cmd():
    """Report registered languages and the external tools PlantUML needs."""
    ok = True

    def line(label, value, required=True):
        nonlocal ok
        found = bool(value)
        if required and not found:
            ok = False
        click.echo(f"{label:<14}{value if found else 'NOT FOUND'}")

    click.echo(f"project root  {paths.project_root()}")
    langs = [name for name in DSL_REGISTRY if name in language_descriptions()]
    line("languages", ", ".join(langs) if len(langs) == len(DSL_REGISTRY) else "", required=True)
    if len(langs) != len(DSL_REGISTRY):
        click.echo("              -> run: pip install -e .")
    line("plantuml jar", render.find_plantuml_jar())
    line("java", render.find_java())
    line("graphviz dot", render.find_dot(), required=False)
    if not render.find_dot():
        click.echo("              (only needed for --layout dot; use --layout smetana without it)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    try:
        main()
    except TextXError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)
