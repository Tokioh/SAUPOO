import abc
from typing import Protocol, Tuple, List
from app.core.models.aspirante import Aspirante
from app.core.models.carrera import Carrera

class ILectorDatos(Protocol):
    """
    Interfaz para un servicio que lee los datos de entrada
    y los convierte en nuestros modelos de dominio (Aspirante, Carrera).
    """
    @abc.abstractmethod
    def cargar_datos(self) -> Tuple[List[Aspirante], List[Carrera]]:
        ...
