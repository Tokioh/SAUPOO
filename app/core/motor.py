from app.core.interfaces.i_lector_datos import ILectorDatos
from app.core.interfaces.i_escritor_resultados import IEscritorResultados
from app.core.interfaces.i_strategy_asignacion import IStrategyAsignacion
from app.core.models.normativa import Normativa
import traceback

class MotorAsignacion:
    """
    El orquestador principal. Recibe las implementaciones de las
    interfaces a través de inyección de dependencias.
    """
    def __init__(
        self,
        lector: ILectorDatos,
        escritor: IEscritorResultados,
        estrategia: IStrategyAsignacion,
        normativa: Normativa
    ):
        self.lector = lector
        self.escritor = escritor
        self.estrategia = estrategia
        self.normativa = normativa
        print("Motor de Asignación inicializado.")

    def ejecutar_proceso(self):
        """Ejecuta el proceso completo de asignación."""
        try:
            print("\n[PASO 1] Cargando datos de entrada...")
            aspirantes, carreras = self.lector.cargar_datos()

            print("\n[PASO 2] Ejecutando estrategia de asignación...")
            resultados = self.estrategia.ejecutar_asignacion(
                aspirantes, carreras, self.normativa
            )

            print("\n[PASO 3] Escribiendo resultados de salida...")
            self.escritor.escribir_resultados(resultados)
            
            print("\n[PROCESO FINALIZADO] El proceso se completó exitosamente.")
            
            if self.normativa.log_reporte:
                print("\nSe generaron las siguientes advertencias durante el proceso:")
                for msg in self.normativa.log_reporte:
                    print(f"- {msg}")

        except Exception as e:
            print(f"\n[ERROR FATAL] El proceso falló: {e}")
            traceback.print_exc()
