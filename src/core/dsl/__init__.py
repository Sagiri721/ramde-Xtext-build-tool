"""Built-in DSL extensions and their registry."""

from .registry import DSL_REGISTRY, dsl_for_model

__all__ = ["DSL_REGISTRY", "dsl_for_model"]