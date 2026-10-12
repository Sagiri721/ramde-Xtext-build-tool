"""PlantUML use-case diagram for a ``UCModel`` (port of ``UseCasePlantUMLConverter``)."""
from __future__ import annotations

from textx import get_model

from ...plantuml.common import Links, escape, header, quote_text, sanitize
from ...plantuml.presentation import PumlRenderer

class UseCasesPumlRenderer(PumlRenderer):

    @staticmethod
    def _actor_id(actor) -> str:
        return "actor_" + sanitize(actor.name)

    @staticmethod
    def _use_case_id(use_case) -> str:
        return "uc_" + sanitize(use_case.name)

    @staticmethod
    def _requirement_id(requirement) -> str:
        req_model = get_model(requirement)
        return f"req_{sanitize(req_model.name)}_{sanitize(requirement.name)}"

    def render(self, model, links: Links | None = None, layout: str = "dot") -> str:
        links = links or Links()
        out = header(layout)
        model_name = model.name or "UCModel"

        actors = list(model.actor)
        # Use cases the model contains, plus any an actor acts on (insertion-ordered, de-duplicated).
        use_cases = dict.fromkeys(model.contains)
        for actor in actors:
            use_cases.update(dict.fromkeys(actor.acts))
        requirements = {}
        for use_case in use_cases:
            requirement = getattr(use_case, "refine", None)
            if requirement is not None:
                requirements.setdefault(self._requirement_id(requirement), requirement)

        # 1. Actors: stick figures, outside the system boundary
        for actor in actors:
            label = links.label(actor, quote_text(actor.name))
            out.append(f'actor "{label}" as {self._actor_id(actor)}')
        out.append("")

        # 2. System boundary with the use cases as ellipses
        out.append(f'rectangle "{quote_text(model_name)}" as uc_model_{sanitize(model_name)} #F4F6F7 {{')
        for use_case in use_cases:
            label = links.label(use_case, quote_text(use_case.name))
            if use_case.description.strip():
                label += "\\n--\\n" + escape(quote_text(use_case.description))
            out.append(f'  usecase "{label}" as {self._use_case_id(use_case)} #D6EAF8')
        out.append("}")
        out.append("")

        # 3. Refined requirements are shown outside the use-case system boundary.
        for requirement_id, requirement in requirements.items():
            req_model = get_model(requirement)
            name = f"{req_model.name}.{requirement.name}"
            label = links.label(requirement, quote_text(name))
            out.append(f'rectangle "{label}" as {requirement_id} #FCF3CF')
        out.append("")

        # 4. Associations and refinement links.
        for actor in actors:
            for use_case in actor.acts:
                out.append(f"{self._actor_id(actor)} --> {self._use_case_id(use_case)}")
        for use_case in use_cases:
            requirement = getattr(use_case, "refine", None)
            if requirement is not None:
                out.append(
                    f"{self._use_case_id(use_case)} ..> "
                    f"{self._requirement_id(requirement)} : refines"
                )

        out.append("@enduml")
        return "\n".join(out)
