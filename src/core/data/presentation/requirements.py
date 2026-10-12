"""PlantUML object diagram for a ``ReqModel`` (port of ``EMFToPlantUMLConverter``)."""
from __future__ import annotations

from ...plantuml.common import Links, escape, header, sanitize
from ...plantuml.presentation import PumlRenderer

class RequirementsPumlRenderer(PumlRenderer):
    #: Node colour per requirement status (same palette as the Eclipse generator).
    STATUS_COLORS = {
        "APPROVED": "#D4EFDF",  # soft green
        "REVIEW": "#FCF3CF",  # soft yellow
        "DRAFT": "#D6EAF8",  # soft blue
        "REJECTED": "#FADBD8",  # soft red
    }
    DEFAULT_COLOR = "#EAECEE"
    RISK_COLOR = "#FADBD8"

    @staticmethod
    def status_color(status: str | None) -> str:
        return RequirementsPumlRenderer.STATUS_COLORS.get(status or "", RequirementsPumlRenderer.DEFAULT_COLOR)

    def render(self, model, links: Links | None = None, layout: str = "dot") -> str:
        links = links or Links()
        out = header(layout)

        # Referenced risks are declared even if they live elsewhere; declared-but-unreferenced
        # risks are drawn too, because an unmitigated risk is exactly what a reader wants to see.
        risks = dict.fromkeys(model.risks)
        for req in model.has:
            risks.update(dict.fromkeys(req.mitigates))

        # 1. Requirements, coloured by status
        for req in model.has:
            out.append(
                f'object "{links.label(req, req.name)}" as {sanitize(req.name)} '
                f"{RequirementsPumlRenderer.status_color(req.status)} {{"
            )
            if req.description.strip():
                out.append(f"  description = {escape(req.description)}")
            if req.status:
                out.append(f"  status = {req.status}")
            if req.priority:
                out.append(f"  priority = {req.priority}")
            if req.type:
                out.append(f"  type = {req.type}")
            if req.verificationMethod:
                out.append(f"  verification = {req.verificationMethod}")
            if req.author.strip():
                out.append(f"  author = {escape(req.author)}")
            if req.risk:
                out.append(f"  riskLevel = {req.risk}")
            out.append("}")
        out.append("")

        # 2. Risks, highlighted in red
        for risk in risks:
            out.append(
                f'object "{links.label(risk, risk.name)}" as risk_{sanitize(risk.name)} '
                f"{RequirementsPumlRenderer.RISK_COLOR} <<Risk>> {{"
            )
            if risk.description.strip():
                out.append(f"  description = {escape(risk.description)}")
            out.append("}")
        out.append("")

        # 3. Relationships
        for req in model.has:
            source = sanitize(req.name)
            for target in req.requirement:
                out.append(f"{source} .> {sanitize(target.name)} : requirement")
            for risk in req.mitigates:
                out.append(f"{source} .> risk_{sanitize(risk.name)} : mitigates")

        out.append("@enduml")
        return "\n".join(out)
