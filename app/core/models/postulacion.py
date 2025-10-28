from dataclasses import dataclass

@dataclass(frozen=True)
class Postulacion:
    """Representa una única elección de carrera de un aspirante."""
    id_carrera: str
    prioridad: int
    nombre_carrera_debug: str # Para facilitar la depuración

@dataclass
class AsignacionResultado:
    """Representa un cupo asignado exitosamente."""
    id_aspirante: str
    puntaje_postulacion: float
    segmento_asignado: str
    prioridad_asignada: int
    id_carrera_asignada: str
    nombre_carrera_asignada: str
    # Campos requeridos por el formato de salida de monitoreo
    periodo: str = "PERIODO_EJEMPLO_2025"
    id_ies: str = "IES_EJEMPLO"
    fecha_postulacion: str = "2025-10-27" # Simulado
    instancia_postulacion: int = 1 # Simulado
    cus_id: str = "CUS_ID_SIMULADO" # Simulado
