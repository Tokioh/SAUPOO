from typing import List, Dict, Any
import pandas as pd
from app.core.models.normativa import Normativa

class ValidadorProceso:
    """
    Clase de ayuda para validar los datos de entrada
    antes de convertirlos en modelos.
    """
    def __init__(self, normativa: Normativa):
        self.normativa = normativa
        self.mapeo_post = normativa.mapeo_columnas_postulaciones
        self.mapeo_oferta = normativa.mapeo_columnas_oferta
        self.mapeo_segmentos = normativa.mapeo_segmentos_cupos

    def validar_columnas_postulaciones(self, df: pd.DataFrame) -> None:
        columnas_necesarias = list(self.mapeo_post.values())
        columnas_faltantes = [col for col in columnas_necesarias if col not in df.columns]
        if columnas_faltantes:
            raise ValueError(f"Archivo de postulaciones inválido. Faltan columnas: {columnas_faltantes}")
        print("Validación de columnas de postulaciones: OK")

    def validar_columnas_oferta(self, df: pd.DataFrame) -> None:
        columnas_necesarias = list(self.mapeo_oferta.values()) + self.mapeo_segmentos
        columnas_faltantes = [col for col in columnas_necesarias if col not in df.columns]
        if columnas_faltantes:
            raise ValueError(f"Archivo de oferta académica inválido. Faltan columnas: {columnas_faltantes}")
        print("Validación de columnas de oferta académica: OK")

    def limpiar_y_validar_postulacion_aspirante(self, df_grupo_aspirante: pd.DataFrame) -> pd.DataFrame:
        """
        Valida las N postulaciones de un aspirante.
        Si tiene más del máximo, ignora y reporta (Punto 3).
        """
        prioridad_col = self.mapeo_post['prioridad']
        
        # Aseguramos que la prioridad sea numérica y ordenamos
        df_grupo_aspirante[prioridad_col] = pd.to_numeric(df_grupo_aspirante[prioridad_col])
        df_ordenado = df_grupo_aspirante.sort_values(by=prioridad_col)
        
        max_post = self.normativa.max_postulaciones
        
        if len(df_ordenado) > max_post:
            id_aspirante = df_ordenado[self.mapeo_post['id_aspirante']].iloc[0]
            df_truncado = df_ordenado.iloc[:max_post]
            df_ignorado = df_ordenado.iloc[max_post:]
            
            carreras_ignoradas = df_ignorado[self.mapeo_post['id_carrera']].tolist()
            self.normativa.reportar_incidencia(
                f"Aspirante {id_aspirante}: Se ignoraron {len(df_ignorado)} postulaciones "
                f"(>{max_post} permitidas). Carreras ignoradas (OFA_ID): {carreras_ignoradas}"
            )
            return df_truncado
            
        return df_ordenado

    def str_a_bool(self, valor: Any) -> bool:
        """Convierte los 'SI'/'NO' o 1/0 del CSV a booleanos."""
        if isinstance(valor, str):
            return valor.strip().upper() == 'SI'
        return bool(int(valor)) if pd.notna(valor) and str(valor).isdigit() else bool(valor)
