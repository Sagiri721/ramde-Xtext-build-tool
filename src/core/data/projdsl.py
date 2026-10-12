"""Requirements DSL extension: defaults, validation, and diagram rendering."""
from __future__ import annotations

from textx import get_location
from textx.exceptions import TextXSemanticError
from .presentation.requirements import RequirementsPumlRenderer
from ..dsl.spec import DSLSpec

REQUIREMENT_DEFAULTS = {
    "status": "DRAFT",
    "priority": "LOW",
    "verificationMethod": "ANALYSIS",
    "type": "FUNCTIONALITY",
    "risk": "LOW",
}


def apply_requirement_defaults(requirement) -> None:
    for attr, default in REQUIREMENT_DEFAULTS.items():
        if not getattr(requirement, attr):
            setattr(requirement, attr, default)


def _check_unique_names(container, children, kind: str) -> None:
    seen = set()
    for child in children:
        if child.name in seen:
            raise TextXSemanticError(
                f'Duplicate {kind} name "{child.name}" in '
                f'{type(container).__name__} "{container.name}".',
                **get_location(child),
            )
        seen.add(child.name)


def check_model(model, metamodel) -> None:
    _check_unique_names(model, model.has, "Requirement")
    _check_unique_names(model, model.risks, "Risk")


def configure(metamodel) -> None:
    metamodel.register_obj_processors({"Requirement": apply_requirement_defaults})
    metamodel.register_model_processor(check_model)

SPEC = DSLSpec(
    name="projdsl",
    pattern="*.projdsl",
    grammar="projdsl.tx",
    root_type="ReqModel",
    description="Requirements DSL (ReqModel / Requirement / Risk).",
    configure=configure,
    renderer=RequirementsPumlRenderer(),
)