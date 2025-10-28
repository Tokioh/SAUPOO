import abc
from typing import Protocol
from app.core.models.aspirante import Aspirante

class IManejadorSegmento(Protocol):
    """
    Interfaz para un manejador de un segmento específico (ej. Merito, Vulnerabilidad).
    """
    @abc.abstractmethod
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        """Verifica si un aspirante pertenece a este segmento."""
        ...

    @abc.abstractmethod
    def get_segmento_key(self) -> str:
        """Retorna la clave del cupo para este segmento (ej. 'OFERTA_MERITO_ACADEMICO')."""
        ...
