import json
from dependency_injector import containers, providers
from app.core.models.normativa import Normativa
from app.core.services.lector_datos import LectorDatosCSV
from app.core.services.escritor_resultados import EscritorResultadosCSV
from app.core.strategy.estrategia_art_52 import EstrategiaAsignacionArt52
from app.core.motor import MotorAsignacion

class Container(containers.DeclarativeContainer):
    """
    Contenedor de Inyección de Dependencias.
    Unimos nuestras clases abstractas
    con sus implementaciones concretas.
    """
    
    # 1. Configuración (Normativa) - Cargada como Singleton
    config = providers.Singleton(
        lambda: json.load(open('config.json', 'r', encoding='utf-8'))
    )
    
    normativa = providers.Singleton(
        Normativa,
        ponderadores=config.provided['ponderadores'],
        puntos_adicionales=config.provided['puntos_adicionales'],
        max_postulaciones=config.provided['parametros_proceso']['max_postulaciones_permitidas'],
        rutas=config.provided['rutas_archivos'],
        mapeo_columnas_oferta=config.provided['mapeo_columnas']['oferta'],
        mapeo_columnas_postulaciones=config.provided['mapeo_columnas']['postulaciones'],
        mapeo_segmentos_cupos=config.provided['mapeo_columnas']['segmentos_cupos']
    )

    # 2. Proveedores de Servicios (Implementaciones)
    lector_datos = providers.Factory(
        LectorDatosCSV,
        normativa=normativa
    )
    
    escritor_resultados = providers.Factory(
        EscritorResultadosCSV,
        normativa=normativa
    )

    # 3. Proveedor de Estrategia
    estrategia_asignacion = providers.Factory(
        EstrategiaAsignacionArt52
    )

    # 4. Proveedor del Motor
    motor = providers.Factory(
        MotorAsignacion,
        lector=lector_datos,
        escritor=escritor_resultados,
        estrategia=estrategia_asignacion,
        normativa=normativa
    )
