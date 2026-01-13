import json
import os
import shutil
from datetime import datetime
from typing import List, Optional
from ..models.ronda import Ronda
from ..models.periodo import PeriodoAcademico, Semestre


class GestorRondas:
    """
    Gestiona el historial de rondas de asignación por período académico.
    
    Responsabilidades:
    - Crear y registrar nuevas rondas
    - Organizar archivos por período en subdirectorios
    - Mantener el historial en un archivo JSON
    - Proporcionar consultas y estadísticas
    
    Estructura de directorios:
        outputs/
        ├── historial_rondas.json
        ├── 2026-1/
        │   ├── ronda_1_20260111_143022_oferta.csv
        │   ├── ronda_1_20260111_143022_postulaciones.csv
        │   └── ronda_1_20260111_143022_resultados.csv
        └── 2026-2/
            └── ...
    """
    
    def __init__(self, directorio_base: str = "outputs"):
        """
        Inicializa el gestor de rondas.
        
        Args:
            directorio_base: Directorio raíz para almacenar resultados
        """
        self.directorio_base = directorio_base
        self.archivo_historial = os.path.join(directorio_base, "historial_rondas.json")
        self._asegurar_directorio()
    
    def _asegurar_directorio(self) -> None:
        """Crea el directorio base si no existe."""
        os.makedirs(self.directorio_base, exist_ok=True)
    
    def _obtener_directorio_periodo(self, periodo: PeriodoAcademico) -> str:
        """Retorna la ruta del directorio para un período específico."""
        return os.path.join(self.directorio_base, str(periodo))
    
    def _asegurar_directorio_periodo(self, periodo: PeriodoAcademico) -> str:
        """Crea y retorna el directorio para un período específico."""
        directorio = self._obtener_directorio_periodo(periodo)
        os.makedirs(directorio, exist_ok=True)
        return directorio
    
    def _cargar_historial(self) -> List[dict]:
        """Carga el historial desde el archivo JSON."""
        if os.path.exists(self.archivo_historial):
            try:
                with open(self.archivo_historial, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _guardar_historial(self, historial: List[dict]) -> None:
        """Guarda el historial en el archivo JSON."""
        with open(self.archivo_historial, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    
    def obtener_siguiente_numero_ronda(self, periodo: PeriodoAcademico) -> int:
        """
        Retorna el número de la siguiente ronda para un período específico.
        
        Args:
            periodo: Período académico
            
        Returns:
            Número de la siguiente ronda (1 si es la primera)
        """
        historial = self._cargar_historial()
        rondas_periodo = [
            r for r in historial 
            if r["periodo"]["anio"] == periodo.anio 
            and r["periodo"]["semestre"] == periodo.semestre.value
        ]
        if not rondas_periodo:
            return 1
        return max(r["numero"] for r in rondas_periodo) + 1
    
    def crear_ronda(
        self, 
        periodo: PeriodoAcademico,
        archivo_oferta: str,
        archivo_postulaciones: str,
        observaciones: Optional[str] = None
    ) -> Ronda:
        """
        Crea una nueva ronda para un período específico.
        
        Copia los archivos de entrada al directorio del período para
        mantener un registro histórico de los datos usados.
        
        Args:
            periodo: Período académico
            archivo_oferta: Ruta al CSV de oferta académica
            archivo_postulaciones: Ruta al CSV de postulaciones
            observaciones: Notas opcionales
            
        Returns:
            Ronda creada (sin registrar aún en el historial)
        """
        numero = self.obtener_siguiente_numero_ronda(periodo)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear directorio del período
        directorio_periodo = self._asegurar_directorio_periodo(periodo)
        
        # Nombres de archivos para esta ronda
        prefijo = f"ronda_{numero}_{timestamp}"
        
        ronda = Ronda(
            numero=numero,
            periodo=periodo,
            fecha_ejecucion=datetime.now(),
            archivo_oferta=f"{prefijo}_oferta.csv",
            archivo_postulaciones=f"{prefijo}_postulaciones.csv",
            archivo_resultados=f"{prefijo}_resultados.csv",
            observaciones=observaciones
        )
        
        # Copiar archivos de entrada al directorio del período
        shutil.copy(archivo_oferta, os.path.join(directorio_periodo, ronda.archivo_oferta))
        shutil.copy(archivo_postulaciones, os.path.join(directorio_periodo, ronda.archivo_postulaciones))
        
        return ronda
    
    def registrar_ronda(self, ronda: Ronda) -> None:
        """
        Registra una ronda completada en el historial.
        
        Args:
            ronda: Ronda a registrar
        """
        historial = self._cargar_historial()
        historial.append(ronda.to_dict())
        self._guardar_historial(historial)
    
    def obtener_historial(self, periodo: Optional[PeriodoAcademico] = None) -> List[Ronda]:
        """
        Retorna las rondas registradas.
        
        Args:
            periodo: Si se especifica, filtra solo ese período
            
        Returns:
            Lista de rondas ordenadas por fecha
        """
        historial = self._cargar_historial()
        
        if periodo:
            historial = [
                r for r in historial
                if r["periodo"]["anio"] == periodo.anio
                and r["periodo"]["semestre"] == periodo.semestre.value
            ]
        
        rondas = [Ronda.from_dict(r) for r in historial]
        return sorted(rondas, key=lambda r: r.fecha_ejecucion)
    
    def obtener_ronda(self, periodo: PeriodoAcademico, numero: int) -> Optional[Ronda]:
        """
        Obtiene una ronda específica por período y número.
        
        Args:
            periodo: Período académico
            numero: Número de la ronda
            
        Returns:
            Ronda encontrada o None
        """
        historial = self._cargar_historial()
        for r in historial:
            if (r["periodo"]["anio"] == periodo.anio 
                and r["periodo"]["semestre"] == periodo.semestre.value
                and r["numero"] == numero):
                return Ronda.from_dict(r)
        return None
    
    def obtener_periodos_disponibles(self) -> List[PeriodoAcademico]:
        """
        Retorna lista de períodos que tienen al menos una ronda.
        
        Returns:
            Lista de períodos ordenados de más reciente a más antiguo
        """
        historial = self._cargar_historial()
        periodos_unicos = set()
        
        for r in historial:
            periodo = PeriodoAcademico.from_dict(r["periodo"])
            periodos_unicos.add(periodo)
        
        return sorted(periodos_unicos, reverse=True)
    
    def obtener_ruta_archivo(self, ronda: Ronda, tipo: str) -> str:
        """
        Retorna la ruta completa de un archivo de la ronda.
        
        Args:
            ronda: La ronda
            tipo: 'oferta', 'postulaciones' o 'resultados'
            
        Returns:
            Ruta absoluta al archivo
            
        Raises:
            ValueError: Si el tipo no es válido
        """
        directorio = self._obtener_directorio_periodo(ronda.periodo)
        
        archivos = {
            "oferta": ronda.archivo_oferta,
            "postulaciones": ronda.archivo_postulaciones,
            "resultados": ronda.archivo_resultados
        }
        
        if tipo not in archivos:
            raise ValueError(f"Tipo de archivo no válido: {tipo}. Use: {list(archivos.keys())}")
        
        return os.path.join(directorio, archivos[tipo])
    
    def obtener_resumen_periodo(self, periodo: PeriodoAcademico) -> dict:
        """
        Retorna un resumen estadístico de todas las rondas de un período.
        
        Args:
            periodo: Período académico
            
        Returns:
            Diccionario con estadísticas agregadas
        """
        rondas = self.obtener_historial(periodo)
        
        if not rondas:
            return {
                "periodo": str(periodo),
                "total_rondas": 0,
                "total_aspirantes_procesados": 0,
                "total_asignados": 0,
                "total_no_asignados": 0,
                "tasa_asignacion_promedio": 0.0
            }
        
        total_aspirantes = sum(r.total_aspirantes for r in rondas)
        total_asignados = sum(r.total_asignados for r in rondas)
        
        return {
            "periodo": str(periodo),
            "total_rondas": len(rondas),
            "total_aspirantes_procesados": total_aspirantes,
            "total_asignados": total_asignados,
            "total_no_asignados": sum(r.total_no_asignados for r in rondas),
            "tasa_asignacion_promedio": round((total_asignados / total_aspirantes * 100) if total_aspirantes > 0 else 0, 2),
            "primera_ronda": rondas[0].fecha_ejecucion.isoformat(),
            "ultima_ronda": rondas[-1].fecha_ejecucion.isoformat()
        }
    
    def eliminar_ronda(self, periodo: PeriodoAcademico, numero: int) -> bool:
        """
        Elimina una ronda del historial y sus archivos asociados.
        
        Args:
            periodo: Período académico
            numero: Número de la ronda
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        ronda = self.obtener_ronda(periodo, numero)
        if not ronda:
            return False
        
        # Eliminar archivos
        for tipo in ["oferta", "postulaciones", "resultados"]:
            try:
                ruta = self.obtener_ruta_archivo(ronda, tipo)
                if os.path.exists(ruta):
                    os.remove(ruta)
            except Exception:
                pass
        
        # Eliminar del historial
        historial = self._cargar_historial()
        historial = [
            r for r in historial
            if not (r["periodo"]["anio"] == periodo.anio 
                   and r["periodo"]["semestre"] == periodo.semestre.value
                   and r["numero"] == numero)
        ]
        self._guardar_historial(historial)
        
        return True
