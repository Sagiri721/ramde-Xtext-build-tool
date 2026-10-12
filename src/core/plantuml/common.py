"""Helpers shared by the PlantUML emitters (ported from EMFToPlantUMLConverter)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from textx import get_location

LINK_STYLES = ("none", "vscode")
LAYOUTS = ("dot", "smetana")


def header(layout: str = "dot") -> list[str]:
    """PlantUML preamble (skin settings) - identical to the Eclipse generator's."""
    lines = ["@startuml"]
    if layout == "smetana":
        # PlantUML's built-in pure-Java layout engine: no Graphviz installation needed.
        lines.append("!pragma layout smetana")
    lines += [
        "skinparam shadowing false",
        "skinparam defaultFontName 'Segoe UI', Arial, sans-serif",
        "skinparam RoundCorner 8",
        "skinparam ArrowColor #2C3E50",
        "skinparam ArrowThickness 1.5",
        "left to right direction",
        "",
    ]
    return lines


def sanitize(identifier: str | None) -> str:
    """Turn a model name into a valid PlantUML alias."""
    if identifier is None:
        return "null"
    return re.sub(r"[^a-zA-Z0-9_]", "_", identifier)


def escape(text: str | None) -> str:
    """Make a (possibly multi-line) string safe for a single PlantUML line."""
    if text is None:
        return ""
    return text.replace("\r", "").replace("\n", "\\n")


def quote_text(text: str | None) -> str:
    """Double quotes would end a PlantUML string; use single quotes instead."""
    return "" if text is None else text.replace('"', "'")


@dataclass(frozen=True)
class Links:
    """How diagram nodes link back to the model source.

    ``none``   - plain labels (default for ``textx generate`` output; no absolute paths).
    ``vscode`` - ``[[vscode://file/<abs path>:<line>:<col> Name]]``. Opening the SVG in a
                 browser and clicking a node jumps to that line in VS Code. This is the
                 replacement for the Eclipse view's "click node -> select in Xtext editor".
    """

    style: str = "none"

    def __post_init__(self):
        if self.style not in LINK_STYLES:
            raise ValueError(f"unknown link style {self.style!r}; choose from {LINK_STYLES}")

    def url(self, obj) -> str | None:
        if self.style == "none":
            return None
        loc = get_location(obj)
        if not loc.get("filename"):
            return None  # model parsed from a string: nothing to jump to
        path = Path(loc["filename"]).resolve().as_posix()
        if not path.startswith("/"):  # Windows drive path "C:/..." -> "/C:/..."
            path = "/" + path
        return f"vscode://file{quote(path, safe='/:')}:{loc['line']}:{loc['col']}"

    def label(self, obj, text: str) -> str:
        """``[[url text]]`` when a link is available, else just ``text``."""
        url = self.url(obj)
        return f"[[{url} {text}]]" if url else text
