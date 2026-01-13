from .interfaces.i_lector_datos import ILectorDatos
from .interfaces.i_escritor_resultados import IEscritorResultados
from .interfaces.i_strategy_asignacion import IStrategyAsignacion
from .services.gestor_rondas import GestorRondas
from .models.ronda import Ronda
from .models.periodo import PeriodoAcademico
from .models.postulacion import AsignacionResultado
from .models.normativa import Normativa
from typing import Optional, Tuple, List


class MotorAsignacion:
    """
    El orquestador principal del proceso de asignación.
    
    Coordina la lectura de datos, ejecución de la estrategia de asignación
    y escritura de resultados. Integra el sistema de rondas para mantener
    un historial de cada proceso de asignación.
    """
    def __init__(
        self,
        lector: ILectorDatos,
        escritor: IEscritorResultados,
        strategy: IStrategyAsignacion,
        normativa: Normativa,
        gestor_rondas: Optional[GestorRondas] = None
    ):
        self.lector = lector
        self.escritor = escritor
        self.strategy = strategy
        self.normativa = normativa
        self.gestor_rondas = gestor_rondas or GestorRondas()
        print("Motor de Asignación inicializado.")

    def ejecutar_ronda(
        self,
        periodo: PeriodoAcademico,
        archivo_oferta: str,
        archivo_postulaciones: str,
        observaciones: Optional[str] = None
    ) -> Tuple[Ronda, List[AsignacionResultado]]:
        """
        Ejecuta una ronda de asignación completa.
        
        Args:
            periodo: Período académico (ej: 2026-1)
            archivo_oferta: Ruta al CSV de oferta académica
            archivo_postulaciones: Ruta al CSV de postulaciones
            observaciones: Notas opcionales sobre la ronda
        
        Returns:
            Tuple con la ronda creada y la lista de resultados
        """
        # Crear nueva ronda (esto también copia los archivos de entrada)
        ronda = self.gestor_rondas.crear_ronda(
            periodo=periodo,
            archivo_oferta=archivo_oferta,
            archivo_postulaciones=archivo_postulaciones,
            observaciones=observaciones
        )
        
        # Leer datos desde los archivos copiados al directorio del período
        ruta_oferta = self.gestor_rondas.obtener_ruta_archivo(ronda, "oferta")
        ruta_postulaciones = self.gestor_rondas.obtener_ruta_archivo(ronda, "postulaciones")
        
        # Usar el lector para cargar los datos
        aspirantes, carreras = self.lector.cargar_datos_desde_rutas(
            ruta_oferta, 
            ruta_postulaciones
        )
        
        # Ejecutar asignación
        resultados = self.strategy.ejecutar_asignacion(aspirantes, carreras, self.normativa)
        
        # Actualizar estadísticas de la ronda
        ronda.total_aspirantes = len(aspirantes)
        ronda.total_asignados = len(resultados)  # Los resultados solo contienen asignados
        ronda.total_no_asignados = ronda.total_aspirantes - ronda.total_asignados
        
        # Guardar resultados
        ruta_resultados = self.gestor_rondas.obtener_ruta_archivo(ronda, "resultados")
        self.escritor.escribir_resultados_en_ruta(resultados, ruta_resultados)
        
        # Registrar ronda en el historial
        self.gestor_rondas.registrar_ronda(ronda)
        
        return ronda, resultados
    
    def obtener_historial_rondas(self, periodo: Optional[PeriodoAcademico] = None) -> List[Ronda]:
        """Retorna el historial de rondas, opcionalmente filtrado por período."""
        return self.gestor_rondas.obtener_historial(periodo)
    
    def obtener_ronda(self, periodo: PeriodoAcademico, numero: int) -> Optional[Ronda]:
        """Obtiene información de una ronda específica."""
        return self.gestor_rondas.obtener_ronda(periodo, numero)
    
    def obtener_periodos(self) -> List[PeriodoAcademico]:
        """Retorna lista de períodos con rondas registradas."""
        return self.gestor_rondas.obtener_periodos_disponibles()

