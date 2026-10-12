"""Discover built-in DSL extension modules from the Python data package."""
from __future__ import annotations

import click
from importlib import import_module
from pkgutil import iter_modules

from .. import data

# Discover DSLs dynamically from the Python package
def _discover_dsls():
    specs = {}
    modules = sorted(iter_modules(data.__path__, f"{data.__name__}."), key=lambda item: item.name)
    for module_info in modules:
        if module_info.ispkg:
            continue
        module = import_module(module_info.name)
        spec = getattr(module, "SPEC", None)
        if spec is None:
            continue
        if spec.name in specs:
            raise ValueError(f"Duplicate DSL name {spec.name!r}")
        specs[spec.name] = spec

    click.echo(f"Discovered DSLs: {', '.join(specs.keys())}")

    return specs


DSL_REGISTRY = _discover_dsls()

def dsl_for_model(model):
    root_type = type(model).__name__
    for spec in DSL_REGISTRY.values():
        if spec.root_type == root_type:
            return spec
    raise ValueError(f"No DSL registered for model type {root_type!r}")