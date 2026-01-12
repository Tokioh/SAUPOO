from typing import List
import pandas as pd
from app.core.interfaces.i_escritor_resultados import IEscritorResultados
from app.core.models.postulacion import AsignacionResultado
from app.core.models.normativa import Normativa

class EscritorResultadosCSV(IEscritorResultados):
    """Implementación que escribe los resultados en el formato de monitoreo CSV."""
    
    def __init__(self, normativa: Normativa):
        self.ruta_salida = normativa.rutas['resultados_asignacion']

    def escribir_resultados(self, resultados: List[AsignacionResultado]) -> None:
        if not resultados:
            print("No se generaron asignaciones. El archivo de salida estará vacío.")
            columnas = self._get_columnas_formato()
            pd.DataFrame(columns=columnas).to_csv(self.ruta_salida, index=False)
            return
            
        df = pd.DataFrame([r.__dict__ for r in resultados])
        df_formateado = self._formatear_para_salida(df)
        
        try:
            df_formateado.to_csv(self.ruta_salida, index=False)
            print(f"Resultados guardados exitosamente en: {self.ruta_salida}")
        except Exception as e:
            print(f"Error fatal al escribir el archivo de resultados: {e}")
            raise

    def _get_columnas_formato(self) -> List[str]:
        # Columnas según el formato de salida de monitoreo especificado
        return [
            "PERIODO", "IES_ID", "IDENTIFICACION", "FECHA_POSTULACION",
            "PUNTAJE_POSTULACION", "SEGMENTO_ASPIRANTE", "INSTANCIA_POSTULACION",
            "PRIORIDAD_ELECCION_CARRERA", "NOMBRE_CARRERA", "OFA_ID", "CUS_ID"
        ]

    def _formatear_para_salida(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajusta el DataFrame interno al formato de salida."""
        mapeo_nombres = {
            "periodo": "PERIODO", "id_ies": "IES_ID", "id_aspirante": "IDENTIFICACION",
            "fecha_postulacion": "FECHA_POSTULACION", "puntaje_postulacion": "PUNTAJE_POSTULACION",
            "segmento_asignado": "SEGMENTO_ASPIRANTE", "instancia_postulacion": "INSTANCIA_POSTULACION",
            "prioridad_asignada": "PRIORIDAD_ELECCION_CARRERA",
            "nombre_carrera_asignada": "NOMBRE_CARRERA", "id_carrera_asignada": "OFA_ID",
            "cus_id": "CUS_ID"
        }
        
        df_renombrado = df.rename(columns=mapeo_nombres)
        columnas_finales = self._get_columnas_formato()
        
        for col in columnas_finales:
            if col not in df_renombrado:
                df_renombrado[col] = None
        
        return df_renombrado[columnas_finales]
