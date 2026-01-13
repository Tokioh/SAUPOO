import abc
from typing import Protocol, List
from app.core.models.postulacion import AsignacionResultado

class IEscritorResultados(Protocol):
    """
    Interfaz para un servicio que toma los resultados de la asignación
    y los guarda en un formato de salida (ej. CSV de monitoreo).
    """
    @abc.abstractmethod
    def escribir_resultados(self, resultados: List[AsignacionResultado]) -> None:
        ...
