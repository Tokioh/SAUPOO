from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Normativa:
    """Almacena las reglas de negocio cargadas desde config.json."""
    ponderadores: Dict[str, float]
    puntos_adicionales: Dict[str, float]
    max_postulaciones: int
    rutas: Dict[str, str]
    mapeo_columnas_oferta: Dict[str, str]
    mapeo_columnas_postulaciones: Dict[str, str]
    mapeo_segmentos_cupos: List[str]
    log_reporte: List[str] = field(default_factory=list)

    def reportar_incidencia(self, mensaje: str):
        """Añade un mensaje de advertencia al log (ej. postulaciones ignoradas)."""
        print(f"[ADVERTENCIA] {mensaje}")
        self.log_reporte.append(mensaje)
