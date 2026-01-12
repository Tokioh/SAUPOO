from app.core.strategy.i_manejador_segmento import IManejadorSegmento
from app.core.models.aspirante import Aspirante

"""
Implementaciones de los manejadores para cada segmento del Art. 52.
Las claves de 'condiciones' y 'segmento_key' provienen del config.json.
"""

class ManejadorPoliticaCuotas(IManejadorSegmento):
    """Segmento 1: Grupo de política de cuotas."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        # Asumimos que cuotas es para 'PUEBLO_NACIONALIDAD'
        return aspirante.condiciones.get("PUEBLO_NACIONALIDAD", False)
    def get_segmento_key(self) -> str:
        return "OFERTA_POLITICA_CUOTAS"

class ManejadorVulnerabilidad(IManejadorSegmento):
    """Segmento 2: Grupo de mayor vulnerabilidad socioeconómica."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        return aspirante.condiciones.get("CONDICION_SOCIOECONOMICA_POBREZA", False)
    def get_segmento_key(self) -> str:
        return "OFERTA_VULNERABILIDAD_SOCIOECONOMICA"

class ManejadorMeritoAcademico(IManejadorSegmento):
    """Segmento 3: Grupo de Mérito Académico."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        return aspirante.condiciones.get("MERITO_ACADEMICO", False)
    def get_segmento_key(self) -> str:
        return "OFERTA_MERITO_ACADEMICO"

class ManejadorOtrosReconocimientos(IManejadorSegmento):
    """Segmento 4: Grupo de Otros Reconocimientos al Mérito."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        return aspirante.condiciones.get("OTROS_RECONOCIMIENTOS", False)
    def get_segmento_key(self) -> str:
        return "OFERTA_OTROS_RECONOCIMIENTOS"

class ManejadorBachilleresPN(IManejadorSegmento):
    """Segmento 5a: Bachilleres (Pueblos y Nacionalidades)."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        es_bachiller_curso = aspirante.condiciones.get("BACHILLER_CURSO_ACTUAL", False)
        es_pn = aspirante.condiciones.get("PUEBLO_NACIONALIDAD", False)
        return es_bachiller_curso and es_pn
    def get_segmento_key(self) -> str:
        return "OFERTA_BACHILLER_P_N"

class ManejadorBachilleresCurso(IManejadorSegmento):
    """Segmento 5b: Bachilleres del último régimen."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        return aspirante.condiciones.get("BACHILLER_CURSO_ACTUAL", False)
    def get_segmento_key(self) -> str:
        return "OFERTA_BACHILLER_CURSO"

class ManejadorGeneral(IManejadorSegmento):
    """Segmento 6: Población general."""
    def cumple_criterio(self, aspirante: Aspirante) -> bool:
        return True # Todos los que quedan pertenecen a este grupo
    def get_segmento_key(self) -> str:
        return "OFERTA_GENERAL"
