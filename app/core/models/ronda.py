from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .periodo import PeriodoAcademico


@dataclass
class Ronda:
    """
    Representa una ronda de asignación de cupos dentro de un período académico.
    
    Cada ronda registra:
    - El número secuencial dentro del período
    - La fecha y hora de ejecución
    - Estadísticas del proceso (aspirantes, asignados, no asignados)
    - Referencias a los archivos de entrada y salida
    
    Attributes:
        numero: Número secuencial de la ronda dentro del período
        periodo: Período académico al que pertenece la ronda
        fecha_ejecucion: Fecha y hora de ejecución de la ronda
        total_aspirantes: Total de aspirantes procesados
        total_asignados: Total de aspirantes que obtuvieron cupo
        total_no_asignados: Total de aspirantes sin cupo asignado
        archivo_oferta: Nombre del archivo de oferta académica usado
        archivo_postulaciones: Nombre del archivo de postulaciones usado
        archivo_resultados: Nombre del archivo de resultados generado
        observaciones: Notas opcionales sobre la ronda
    """
    numero: int
    periodo: PeriodoAcademico
    fecha_ejecucion: datetime = field(default_factory=datetime.now)
    total_aspirantes: int = 0
    total_asignados: int = 0
    total_no_asignados: int = 0
    archivo_oferta: str = ""
    archivo_postulaciones: str = ""
    archivo_resultados: str = ""
    observaciones: Optional[str] = None
    
    @property
    def identificador(self) -> str:
        """Retorna identificador único: periodo + número de ronda (ej: '2026-1_R1')."""
        return f"{self.periodo}_R{self.numero}"
    
    @property
    def tasa_asignacion(self) -> float:
        """Retorna el porcentaje de aspirantes asignados."""
        if self.total_aspirantes == 0:
            return 0.0
        return (self.total_asignados / self.total_aspirantes) * 100
    
    def to_dict(self) -> dict:
        """Convierte la ronda a diccionario para serialización JSON."""
        return {
            "numero": self.numero,
            "periodo": self.periodo.to_dict(),
            "periodo_str": str(self.periodo),
            "identificador": self.identificador,
            "fecha_ejecucion": self.fecha_ejecucion.isoformat(),
            "total_aspirantes": self.total_aspirantes,
            "total_asignados": self.total_asignados,
            "total_no_asignados": self.total_no_asignados,
            "tasa_asignacion": round(self.tasa_asignacion, 2),
            "archivo_oferta": self.archivo_oferta,
            "archivo_postulaciones": self.archivo_postulaciones,
            "archivo_resultados": self.archivo_resultados,
            "observaciones": self.observaciones
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Ronda":
        """Crea una Ronda desde un diccionario."""
        return cls(
            numero=data["numero"],
            periodo=PeriodoAcademico.from_dict(data["periodo"]),
            fecha_ejecucion=datetime.fromisoformat(data["fecha_ejecucion"]),
            total_aspirantes=data.get("total_aspirantes", 0),
            total_asignados=data.get("total_asignados", 0),
            total_no_asignados=data.get("total_no_asignados", 0),
            archivo_oferta=data.get("archivo_oferta", ""),
            archivo_postulaciones=data.get("archivo_postulaciones", ""),
            archivo_resultados=data.get("archivo_resultados", ""),
            observaciones=data.get("observaciones")
        )
