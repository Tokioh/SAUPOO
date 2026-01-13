import abc
from typing import Protocol, List
from app.core.models.aspirante import Aspirante
from app.core.models.carrera import Carrera
from app.core.models.normativa import Normativa
from app.core.models.postulacion import AsignacionResultado

class IStrategyAsignacion(Protocol):
    """
    Interfaz para la estrategia de asignación de cupos.
    Este es el núcleo de la lógica de negocio (ej. Art. 52).
    """
    @abc.abstractmethod
    def ejecutar_asignacion(
        self,
        aspirantes: List[Aspirante],
        carreras: List[Carrera],
        normativa: Normativa
    ) -> List[AsignacionResultado]:
        ...
