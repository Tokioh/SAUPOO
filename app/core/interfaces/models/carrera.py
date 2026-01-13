from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Carrera:
    """Representa una carrera y sus cupos segmentados."""
    id: str
    nombre: str
    # Almacena los cupos por segmento: {"OFERTA_POLITICA_CUOTAS": 10, ...}
    cupos_segmentados: Dict[str, int] = field(default_factory=dict)
    cupos_totales: int = 0
    cupos_asignados: int = 0

    def __post_init__(self):
        self.cupos_totales = sum(self.cupos_segmentados.values())

    def asignar_cupo(self, segmento_key: str) -> bool:
        """
        Intenta asignar un cupo en un segmento específico.
        Retorna True si fue exitoso, False si no hay cupos en ese segmento.
        """
        cupos_disponibles = self.cupos_segmentados.get(segmento_key, 0)
        
        if cupos_disponibles > 0:
            self.cupos_segmentados[segmento_key] -= 1
            self.cupos_asignados += 1
            return True
        return False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Carrera) and self.id == other.id
