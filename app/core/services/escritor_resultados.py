import csv
from typing import List
from dataclasses import asdict
from app.core.models.postulacion import AsignacionResultado
from app.core.models.normativa import Normativa


class EscritorResultadosCSV:
    """Escribe la lista de AsignacionResultado a un CSV de salida."""
    def __init__(self, normativa: Normativa):
        self.normativa = normativa

    def escribir_resultados(self, resultados: List[AsignacionResultado]) -> None:
        ruta = self.normativa.rutas.get('resultados_asignacion')
        if not ruta:
            self.normativa.reportar_incidencia("No se encontró la ruta de resultados en la normativa.")
            return

        # Convertir dataclasses a dicts
        rows = [asdict(r) for r in resultados]

        if not rows:
            # Crear archivo vacío con cabeceras mínimas
            try:
                with open(ruta, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['id_aspirante', 'id_carrera_asignada', 'nombre_carrera_asignada', 'segmento_asignado', 'puntaje_postulacion', 'prioridad_asignada'])
            except Exception as e:
                self.normativa.reportar_incidencia(f"Error escribiendo archivo de resultados vacío: {e}")
            return

        fieldnames = list(rows[0].keys())
        try:
            with open(ruta, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)
        except Exception as e:
            self.normativa.reportar_incidencia(f"Error escribiendo resultados: {e}")
