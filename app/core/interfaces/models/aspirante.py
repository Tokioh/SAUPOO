from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.core.models.postulacion import Postulacion
from app.core.models.normativa import Normativa

@dataclass
class Aspirante:
    """Representa a un aspirante con sus datos y postulaciones."""
    id: str
    puntaje_antecedentes: float
    puntaje_evaluacion: float
    
    # Almacena todas las columnas booleanas (CONDICION_SOCIO..., RURALIDAD, etc.)
    condiciones: Dict[str, bool] = field(default_factory=dict)
    
    postulaciones: List[Postulacion] = field(default_factory=list)
    puntaje_postulacion: float = 0.0

    def calcular_puntaje_postulacion(self, normativa: Normativa) -> None:
        """
        Calcula el puntaje final de postulación según la normativa (Art. 47 y 49).
        """
        # 1. Componente Ponderado
        pond_eval = self.puntaje_evaluacion * normativa.ponderadores.get("EVALUACION_CAPACIDAD", 0.5)
        pond_ant = self.puntaje_antecedentes * normativa.ponderadores.get("ANTECEDENTE_ACADEMICO", 0.5)
        puntaje_base = pond_eval + pond_ant

        # 2. Puntos Adicionales (Acción Afirmativa)
        puntos_adicionales = 0.0
        
        # Mapeo de condiciones del aspirante a claves de puntos en la normativa
        mapeo_puntos = {
            "CONDICION_SOCIOECONOMICA_POBREZA": "CONDICION_SOCIOECONOMICA_POBREZA",
            "RURALIDAD": "RURALIDAD",
            "TERRITORIALIDAD": "TERRITORIALIDAD",
            "PUEBLO_NACIONALIDAD": "PUEBLO_NACIONALIDAD"
        }
        
        for key_condicion, key_puntos in mapeo_puntos.items():
             if self.condiciones.get(key_condicion, False):
                puntos_adicionales += normativa.puntos_adicionales.get(key_puntos, 0)

        # 2.e. Condiciones de Vulnerabilidad (Máx 35 pts)
        puntos_vulnerabilidad = 0.0
        base_vulnerabilidad = normativa.puntos_adicionales.get("VULNERABILIDAD_BASE", 5)
        
        claves_vulnerabilidad = [
            "PERSONA_CON_DISCAPACIDAD", "BENEFICIARIO_BONO_JOAQUIN",
            "VICTIMA_VIOLENCIA_GENERO", "MIGRANTE_RETORNADO",
            "HIJO_VICTIMA_FEMICIDIO", "ENFERMEDAD_CATASTROFICA",
            "ACOGIMIENTO_INSTITUCIONAL"
        ]
        
        for key in claves_vulnerabilidad:
            if self.condiciones.get(key, False):
                puntos_vulnerabilidad += base_vulnerabilidad
        
        max_vulnerabilidad = normativa.puntos_adicionales.get("VULNERABILIDAD_MAX", 35)
        puntos_adicionales += min(puntos_vulnerabilidad, max_vulnerabilidad)

        # 3. Cálculo Final
        self.puntaje_postulacion = min(round(puntaje_base + puntos_adicionales, 2), 1000.0)

    def get_postulaciones_ordenadas(self) -> List[Postulacion]:
        """Retorna la lista de postulaciones ordenada por prioridad."""
        return sorted(self.postulaciones, key=lambda p: p.prioridad)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Aspirante) and self.id == other.id
