"""textX language entry points generated from the DSL registry."""
from __future__ import annotations

from textx import language, metamodel_from_file

from . import paths
from .dsl import DSL_REGISTRY


def _language_entry_point(spec):
    def metamodel_factory():
        # Match keywords as whole words, so enum literal LOW cannot match LOWER.
        metamodel = metamodel_from_file(
            str(paths.metamodels_dir() / spec.grammar), autokwd=True
        )
        spec.configure(metamodel)
        return metamodel

    metamodel_factory.__doc__ = spec.description
    return language(spec.name, spec.pattern)(metamodel_factory)


for _spec in DSL_REGISTRY.values():
    globals()[_spec.name] = _language_entry_point(_spec)

