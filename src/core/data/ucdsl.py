"""Use-case DSL extension: validation, requirement scoping, and diagrams."""
from __future__ import annotations

import difflib
from pathlib import Path
from .presentation.usecases import UseCasesPumlRenderer
from textx import get_location, get_model, metamodel_for_language, textx_isinstance
from textx.exceptions import TextXError, TextXSemanticError

from .. import paths
from ..dsl.spec import DSLSpec

_CACHE: dict[Path, tuple[tuple[int, int], object]] = {}


def _load_projdsl(path: Path):
    stat = path.stat()
    stamp = (stat.st_mtime_ns, stat.st_size)
    cached = _CACHE.get(path)
    if cached and cached[0] == stamp:
        return cached[1]
    model = metamodel_for_language("projdsl").model_from_file(str(path))
    _CACHE[path] = (stamp, model)
    return model


def clear_cache() -> None:
    _CACHE.clear()


def qualified_children(req_model):
    for child in (*req_model.has, *req_model.risks):
        yield f"{req_model.name}.{child.name}", child


class QualifiedRequirementScope:
    def __init__(self):
        self.pattern = "*.projdsl"

    def __call__(self, obj, attr, obj_ref):
        wanted = obj_ref.obj_name
        model = get_model(obj)

        matches, known, skipped = [], [], []
        for path in paths.workspace_files(model._tx_filename, self.pattern):
            try:
                other = _load_projdsl(path)
            except TextXError as exc:
                skipped.append((path.name, str(exc).splitlines()[0]))
                continue
            for qname, child in qualified_children(other):
                if textx_isinstance(child, obj_ref.cls):
                    known.append(qname)
                    if qname == wanted:
                        matches.append((path, child))

        if len(matches) == 1:
            return matches[0][1]

        line, col = model._tx_parser.pos_to_linecol(obj_ref.position)
        if matches:
            where = ", ".join(path.name for path, _ in matches)
            message = f'Ambiguous {obj_ref.cls.__name__} reference "{wanted}": defined in {where}.'
        else:
            message = f'Unknown {obj_ref.cls.__name__} "{wanted}".'
            if "." not in wanted:
                message += (
                    " References to other files must be qualified as "
                    f'"<ReqModel>.<{obj_ref.cls.__name__}>" and written as a string.'
                )
            close = difflib.get_close_matches(wanted, dict.fromkeys(known), n=3)
            if close:
                message += " Did you mean: " + ", ".join(f'"{name}"' for name in close) + "?"
            for name, reason in skipped:
                message += f" (skipped {name}: {reason})"
        raise TextXSemanticError(message, line=line, col=col, filename=model._tx_filename)


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
    _check_unique_names(model, model.contains, "UseCase")
    _check_unique_names(model, model.actor, "Actor")


def configure(metamodel) -> None:
    metamodel.register_scope_providers({"UseCase.refine": QualifiedRequirementScope()})
    metamodel.register_model_processor(check_model)


SPEC = DSLSpec(
    name="ucdsl",
    pattern="*.ucdsl",
    grammar="ucdsl.tx",
    root_type="UCModel",
    description="Use-case DSL (UCModel / UseCase / Actor).",
    configure=configure,
    renderer=UseCasesPumlRenderer(),
)