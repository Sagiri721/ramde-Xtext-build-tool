"""Puml render abstract class"""
from abc import ABC, abstractmethod

from core.plantuml.common import Links

class PumlRenderer(ABC):
    @abstractmethod
    def render(self, model, links: Links | None = None, layout: str = "dot") -> str:
        """Render the given PlantUML code to the specified output file."""
        pass