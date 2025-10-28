import pandas as pd
from typing import List, Tuple, Dict
from app.core.models.aspirante import Aspirante
from app.core.models.carrera import Carrera
from app.core.models.postulacion import Postulacion
from app.core.models.normativa import Normativa


class LectorDatosCSV:
    """Implementación simple que lee los CSV de entrada según la normativa."""
    def __init__(self, normativa: Normativa):
        self.normativa = normativa

    def cargar_datos(self) -> Tuple[List[Aspirante], List[Carrera]]:
        rutas = self.normativa.rutas

        # Leer oferta académica
        try:
            df_oferta = pd.read_csv(rutas['oferta_academica'], dtype=str).fillna(0)
        except Exception as e:
            self.normativa.reportar_incidencia(f"No se pudo leer oferta_academica: {e}")
            df_oferta = pd.DataFrame()

        carreras: List[Carrera] = []
        id_col = self.normativa.mapeo_columnas_oferta.get('id_carrera')
        nombre_col = self.normativa.mapeo_columnas_oferta.get('nombre_carrera')

        for _, row in df_oferta.iterrows():
            try:
                id_val = str(row.get(id_col, '')).strip()
                name_val = str(row.get(nombre_col, '')).strip()
                cupos_segmentados: Dict[str, int] = {}
                for seg in self.normativa.mapeo_segmentos_cupos:
                    try:
                        cup = int(float(row.get(seg, 0) or 0))
                    except Exception:
                        cup = 0
                    cupos_segmentados[seg] = cup

                carrera = Carrera(id=id_val, nombre=name_val, cupos_segmentados=cupos_segmentados)
                carreras.append(carrera)
            except Exception as e:
                self.normativa.reportar_incidencia(f"Error parseando fila de oferta: {e}")

        # Leer matriz de postulaciones
        try:
            df_post = pd.read_csv(rutas['matriz_postulaciones'], dtype=str).fillna("")
        except Exception as e:
            self.normativa.reportar_incidencia(f"No se pudo leer matriz_postulaciones: {e}")
            df_post = pd.DataFrame()

        aspirantes: List[Aspirante] = []

        mapping = self.normativa.mapeo_columnas_postulaciones
        # Agrupar por identificacion
        if not df_post.empty and mapping.get('id_aspirante') in df_post.columns:
            grouped = df_post.groupby(mapping['id_aspirante'])
            for aspirante_id, group in grouped:
                try:
                    # Tomar la primera fila para campos del aspirante
                    first = group.iloc[0]
                    puntaje_ant = self._parse_float(first.get(mapping.get('antecedentes', ''), 0))
                    puntaje_eval = self._parse_float(first.get(mapping.get('evaluacion', ''), 0))

                    # condiciones booleanas
                    condiciones: Dict[str, bool] = {}
                    for key, col in mapping.items():
                        if key in [
                            'id_aspirante', 'id_carrera', 'prioridad',
                            'antecedentes', 'evaluacion'
                        ]:
                            continue
                        if col in df_post.columns:
                            val = first.get(col, "")
                            condiciones[key.upper()] = self._parse_bool(val)

                    aspirante = Aspirante(
                        id=str(aspirante_id),
                        puntaje_antecedentes=puntaje_ant,
                        puntaje_evaluacion=puntaje_eval,
                        condiciones=condiciones
                    )

                    # Añadir postulaciones del aspirante
                    postulaciones = []
                    for _, row in group.iterrows():
                        id_carrera = str(row.get(mapping.get('id_carrera', ''), '')).strip()
                        prioridad = int(self._parse_float(row.get(mapping.get('prioridad', ''), 0)))
                        nombre_debug = id_carrera
                        # intentar encontrar nombre en df_oferta
                        if id_col in df_oferta.columns and nombre_col in df_oferta.columns:
                            find = df_oferta[df_oferta[id_col].astype(str) == str(id_carrera)]
                            if not find.empty:
                                nombre_debug = str(find.iloc[0][nombre_col])

                        postulacion = Postulacion(id_carrera=id_carrera, prioridad=prioridad, nombre_carrera_debug=nombre_debug)
                        postulaciones.append(postulacion)

                    aspirante.postulaciones = sorted(postulaciones, key=lambda p: p.prioridad)
                    aspirantes.append(aspirante)
                except Exception as e:
                    self.normativa.reportar_incidencia(f"Error construyendo aspirante {aspirante_id}: {e}")
        else:
            # Si no hay datos, retornar listas vacías
            if df_post.empty:
                self.normativa.reportar_incidencia("Archivo de postulaciones vacío o no encontrado.")
            else:
                self.normativa.reportar_incidencia("Columnas de postulaciones no coinciden con el mapeo.")

        return aspirantes, carreras

    def _parse_float(self, v):
        try:
            return float(str(v).replace(',', '.'))
        except Exception:
            return 0.0

    def _parse_bool(self, v) -> bool:
        if v is None:
            return False
        s = str(v).strip().lower()
        return s in ('1', 'true', 'yes', 'si')
