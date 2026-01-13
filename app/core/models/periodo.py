from dataclasses import dataclass
from enum import Enum


class Semestre(Enum):
    """Representa los semestres académicos del año."""
    PRIMERO = 1
    SEGUNDO = 2
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class PeriodoAcademico:
    """
    Representa un período académico (ej: 2026-1, 2026-2).
    
    Attributes:
        anio: Año del período académico
        semestre: Semestre (1 o 2)
    """
    anio: int
    semestre: Semestre
    
    def __str__(self) -> str:
        """Retorna representación string del período (ej: '2026-1')."""
        return f"{self.anio}-{self.semestre.value}"
    
    def to_dict(self) -> dict:
        """Convierte el período a diccionario para serialización."""
        return {
            "anio": self.anio,
            "semestre": self.semestre.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PeriodoAcademico":
        """Crea un PeriodoAcademico desde un diccionario."""
        return cls(
            anio=data["anio"],
            semestre=Semestre(data["semestre"])
        )
    
    @classmethod
    def from_string(cls, periodo_str: str) -> "PeriodoAcademico":
        """
        Crea un período desde string formato '2026-1'.
        
        Args:
            periodo_str: String en formato 'YYYY-S' (ej: '2026-1')
        
        Returns:
            PeriodoAcademico correspondiente
        """
        partes = periodo_str.split("-")
        return cls(
            anio=int(partes[0]),
            semestre=Semestre(int(partes[1]))
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, PeriodoAcademico):
            return False
        return self.anio == other.anio and self.semestre == other.semestre
    
    def __hash__(self) -> int:
        return hash((self.anio, self.semestre.value))
    
    def __lt__(self, other) -> bool:
        """Permite ordenar períodos cronológicamente."""
        if not isinstance(other, PeriodoAcademico):
            return NotImplemented
        if self.anio != other.anio:
            return self.anio < other.anio
        return self.semestre.value < other.semestre.value
