"""Python descriptor for a built-in DSL extension."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from ..plantuml.presentation import PumlRenderer 


@dataclass(frozen=True)
class DSLSpec:
    name: str
    pattern: str
    grammar: str
    root_type: str
    description: str
    configure: Callable
    renderer: PumlRenderer