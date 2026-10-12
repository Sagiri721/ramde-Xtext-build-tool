from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from .. import paths

_EXE = ".exe" if sys.platform == "win32" else ""


class RenderError(RuntimeError):
    """PlantUML (or one of its prerequisites) is missing or rejected the diagram."""


def find_plantuml_jar() -> Path | None:
    env = os.environ.get("PLANTUML_JAR")
    if env:
        return Path(env) if Path(env).is_file() else None
    jars = sorted(paths.tools_dir().glob("plantuml*.jar"))
    return jars[-1] if jars else None


def find_java() -> str | None:
    java_home = os.environ.get("JAVA_HOME")
    candidates = [
        Path(java_home) / "bin" / f"java{_EXE}" if java_home else None,
        paths.tools_dir() / "jre" / "bin" / f"java{_EXE}",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return str(candidate)
    return shutil.which("java")


def find_dot() -> str | None:
    env = os.environ.get("GRAPHVIZ_DOT")
    if env and Path(env).is_file():
        return env
    bundled = paths.tools_dir() / "graphviz" / "bin" / f"dot{_EXE}"
    if bundled.is_file():
        return str(bundled)
    return shutil.which("dot")


def render_svg(plantuml_source: str, *, timeout: float = 120) -> str:
    """Render PlantUML text to an SVG string. Raises :class:`RenderError` on failure."""
    jar = find_plantuml_jar()
    if jar is None:
        raise RenderError(
            "PlantUML jar not found. Put it in tools/ (e.g. tools/plantuml.jar) "
            "or set PLANTUML_JAR."
        )
    java = find_java()
    if java is None:
        raise RenderError("Java not found. Install a JRE, set JAVA_HOME, or use tools/jre/.")

    env = os.environ.copy()
    dot = find_dot()
    if dot:
        env["GRAPHVIZ_DOT"] = dot

    cmd = [java, "-Djava.awt.headless=true", "-jar", str(jar), "-pipe", "-tsvg", "-charset", "UTF-8"]
    try:
        proc = subprocess.run(
            cmd, input=plantuml_source.encode("utf-8"), capture_output=True, env=env, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise RenderError(f"PlantUML timed out after {timeout:.0f}s") from exc

    if proc.returncode != 0:  # PlantUML exits with 200 on syntax errors (and still emits an error SVG)
        detail = proc.stderr.decode("utf-8", "replace").strip() or "no details"
        if dot is None and "dot" in detail.lower():
            detail += "\nGraphviz 'dot' not found: install it, put it in tools/graphviz/, or use --layout smetana."
        raise RenderError(f"PlantUML failed (exit {proc.returncode}): {detail}")
    return proc.stdout.decode("utf-8")
