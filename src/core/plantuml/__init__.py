"""PlantUML generation dispatched through the DSL extension registry."""
from __future__ import annotations

from .common import LAYOUTS, LINK_STYLES, Links
from .render import RenderError, render_svg

__all__ = [
    "LAYOUTS",
    "LINK_STYLES",
    "Links",
    "RenderError",
    "render_svg",
    "requirements_to_plantuml",
    "usecases_to_plantuml",
    "to_plantuml",
]


def to_plantuml(model, links: Links | None = None, layout: str = "dot") -> str:
    """PlantUML source for a model, chosen by its registered DSL."""
    from ..dsl import dsl_for_model

    return dsl_for_model(model).renderer.render(model, links, layout)
