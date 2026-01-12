from typing import List, Dict, Set
from app.core.interfaces.i_strategy_asignacion import IStrategyAsignacion
from app.core.models.aspirante import Aspirante
from app.core.models.carrera import Carrera
from app.core.models.normativa import Normativa
from app.core.models.postulacion import AsignacionResultado
from app.core.strategy.manejadores import (
    ManejadorPoliticaCuotas, ManejadorVulnerabilidad, ManejadorMeritoAcademico,
    ManejadorOtrosReconocimientos, ManejadorBachilleresPN,
    ManejadorBachilleresCurso, ManejadorGeneral
)

class EstrategiaAsignacionArt52(IStrategyAsignacion):
    """
    Implementación de la estrategia de asignación basada en el Art. 52,
    procesando segmentos en orden.
    """
    def __init__(self):
        # El orden de esta lista es la prioridad de los segmentos
        self.manejadores_segmento = [
            ManejadorPoliticaCuotas(),
            ManejadorVulnerabilidad(),
            ManejadorMeritoAcademico(),
            ManejadorOtrosReconocimientos(),
            ManejadorBachilleresPN(),
            ManejadorBachilleresCurso(),
            ManejadorGeneral()
        ]
        print("Estrategia de Asignación Art. 52 inicializada.")

    def ejecutar_asignacion(
        self,
        aspirantes: List[Aspirante],
        carreras: List[Carrera],
        normativa: Normativa
    ) -> List[AsignacionResultado]:
        
        print("Iniciando proceso de asignación...")

        # 1. Calcular puntaje de postulación para todos
        for a in aspirantes:
            a.calcular_puntaje_postulacion(normativa)
        print("Puntajes de postulación calculados.")

        # 2. Preparar estructuras de datos
        aspirantes_sin_asignar_ids: Set[str] = {a.id for a in aspirantes}
        aspirantes_dict: Dict[str, Aspirante] = {a.id: a for a in aspirantes}
        carreras_dict: Dict[str, Carrera] = {c.id: c for c in carreras}
        resultados_finales: List[AsignacionResultado] = []

        # 3. Iterar por cada segmento (manejador) en orden de prioridad
        for i, manejador in enumerate(self.manejadores_segmento):
            segmento_key = manejador.get_segmento_key()
            print(f"\n--- Procesando Segmento {i+1}: {segmento_key} ---")
            
            # 3.a. Obtener aspirantes que aplican a este segmento Y aún no tienen cupo
            aspirantes_del_segmento = []
            for aspirante_id in list(aspirantes_sin_asignar_ids):
                aspirante = aspirantes_dict[aspirante_id]
                if manejador.cumple_criterio(aspirante):
                    aspirantes_del_segmento.append(aspirante)
            
            if not aspirantes_del_segmento:
                print(f"No hay aspirantes elegibles o sin asignar para este segmento.")
                continue

            # 3.b. Ordenar por mérito (puntaje de postulación)
            aspirantes_del_segmento.sort(key=lambda a: a.puntaje_postulacion, reverse=True)
            print(f"Procesando {len(aspirantes_del_segmento)} aspirantes para este segmento...")

            # 3.c. Intentar asignar cupo para cada aspirante en el segmento
            for aspirante in aspirantes_del_segmento:
                
                # Intentar asignar al aspirante en una de sus N prioridades
                for postulacion in aspirante.get_postulaciones_ordenadas():
                    carrera = carreras_dict.get(postulacion.id_carrera)
                    
                    if not carrera:
                        normativa.reportar_incidencia(f"Aspirante {aspirante.id}: Postulación a carrera inexistente (OFA_ID: {postulacion.id_carrera}).")
                        continue

                    # Intentar tomar un cupo de ESTE segmento
                    if carrera.asignar_cupo(segmento_key):
                        # ¡ÉXITO!
                        resultado = AsignacionResultado(
                            id_aspirante=aspirante.id,
                            puntaje_postulacion=aspirante.puntaje_postulacion,
                            segmento_asignado=segmento_key,
                            prioridad_asignada=postulacion.prioridad,
                            id_carrera_asignada=carrera.id,
                            nombre_carrera_asignada=carrera.nombre
                        )
                        resultados_finales.append(resultado)
                        aspirantes_sin_asignar_ids.remove(aspirante.id) 
                        break # Salir del bucle de prioridades
                
                # Si el aspirante no fue asignado (break no se ejecutó),
                # no se quita de 'aspirantes_sin_asignar_ids'
                # y será procesado por el siguiente segmento si califica.

        print(f"\n--- Asignación Finalizada ---")
        print(f"Total de cupos asignados: {len(resultados_finales)}")
        print(f"Total de aspirantes sin cupo: {len(aspirantes_sin_asignar_ids)}")
        
        return resultados_finales
