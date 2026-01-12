from typing import Tuple, List, Dict, Any
import pandas as pd
from app.core.interfaces.i_lector_datos import ILectorDatos
from app.core.models.aspirante import Aspirante
from app.core.models.carrera import Carrera
from app.core.models.postulacion import Postulacion
from app.core.models.normativa import Normativa
from app.core.services.validador_proceso import ValidadorProceso

class LectorDatosCSV(ILectorDatos):
    """Implementación de ILectorDatos que lee desde archivos CSV."""
    
    def __init__(self, normativa: Normativa):
        self.normativa = normativa
        self.validador = ValidadorProceso(normativa)
        self.ruta_oferta = normativa.rutas['oferta_academica']
        self.ruta_postulaciones = normativa.rutas['matriz_postulaciones']
        self.mapeo_post = normativa.mapeo_columnas_postulaciones
        self.mapeo_oferta = normativa.mapeo_columnas_oferta
        self.mapeo_segmentos = normativa.mapeo_segmentos_cupos

    def cargar_datos(self) -> Tuple[List[Aspirante], List[Carrera]]:
        try:
            df_oferta = pd.read_csv(self.ruta_oferta)
            df_postulaciones = pd.read_csv(self.ruta_postulaciones)
        except FileNotFoundError as e:
            print(f"Error fatal: No se encontró el archivo {e.filename}")
            raise
        
        self.validador.validar_columnas_oferta(df_oferta)
        self.validador.validar_columnas_postulaciones(df_postulaciones)
        
        carreras = self._crear_carreras(df_oferta)
        aspirantes = self._crear_aspirantes(df_postulaciones, df_oferta)
        
        print(f"Carga de datos finalizada: {len(aspirantes)} aspirantes y {len(carreras)} carreras.")
        return aspirantes, carreras

    def _crear_carreras(self, df_oferta: pd.DataFrame) -> List[Carrera]:
        carreras = []
        for _, fila in df_oferta.iterrows():
            cupos_segmentados = {}
            for key_segmento in self.mapeo_segmentos:
                cupos_segmentados[key_segmento] = int(fila[key_segmento])
            
            carrera = Carrera(
                id=str(fila[self.mapeo_oferta['id_carrera']]),
                nombre=fila[self.mapeo_oferta['nombre_carrera']],
                cupos_segmentados=cupos_segmentados
            )
            carreras.append(carrera)
        return carreras

    def _crear_aspirantes(self, df_postulaciones: pd.DataFrame, df_oferta: pd.DataFrame) -> List[Aspirante]:
        aspirantes = []
        mapa_nombres_carrera = df_oferta.set_index(self.mapeo_oferta['id_carrera'])[self.mapeo_oferta['nombre_carrera']].to_dict()
        id_aspirante_col = self.mapeo_post['id_aspirante']

        for id_aspirante, grupo in df_postulaciones.groupby(id_aspirante_col):
            grupo_validado = self.validador.limpiar_y_validar_postulacion_aspirante(grupo)
            fila_base = grupo_validado.iloc[0]
            
            condiciones = {}
            for key_mapeo, col_csv in self.mapeo_post.items():
                if key_mapeo not in ['id_aspirante', 'id_carrera', 'prioridad', 'antecedentes', 'evaluacion']:
                    condiciones[col_csv] = self.validador.str_a_bool(fila_base.get(col_csv, False))
            
            aspirante = Aspirante(
                id=str(id_aspirante),
                puntaje_antecedentes=float(fila_base[self.mapeo_post['antecedentes']]),
                puntaje_evaluacion=float(fila_base[self.mapeo_post['evaluacion']]),
                condiciones=condiciones
            )
            
            for _, fila_postulacion in grupo_validado.iterrows():
                id_carrera = str(fila_postulacion[self.mapeo_post['id_carrera']])
                aspirante.postulaciones.append(
                    Postulacion(
                        id_carrera=id_carrera,
                        prioridad=int(fila_postulacion[self.mapeo_post['prioridad']]),
                        nombre_carrera_debug=mapa_nombres_carrera.get(id_carrera, "CARRERA_DESCONOCIDA")
                    )
                )
            aspirantes.append(aspirante)
        return aspirantes
