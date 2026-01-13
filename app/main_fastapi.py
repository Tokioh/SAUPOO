import os
import shutil
import traceback
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from contextlib import asynccontextmanager

from .core.container import Container
from .core.models.periodo import PeriodoAcademico, Semestre

# Rutas absolutas
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp_uploads"
WEB_DIR = BASE_DIR / "web"

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(TEMP_DIR, exist_ok=True)
    yield

app = FastAPI(
    title="SAUPOO - Sistema de Asignación Universitaria",
    description="API para el sistema de asignación de cupos universitarios",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Container global para endpoints legacy
container = Container()


# ============================================
# Rutas para archivos estáticos
# ============================================

@app.get("/")
async def root():
    return FileResponse(WEB_DIR / "index.html", media_type="text/html")


@app.get("/css/{filename}")
async def serve_css(filename: str):
    css_path = WEB_DIR / "css" / filename
    if not css_path.exists():
        raise HTTPException(status_code=404, detail="CSS file not found")
    
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return Response(content=content, media_type="text/css; charset=utf-8")


@app.get("/js/{filename}")
async def serve_js(filename: str):
    js_path = WEB_DIR / "js" / filename
    if not js_path.exists():
        raise HTTPException(status_code=404, detail="JS file not found")
    
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return Response(content=content, media_type="application/javascript; charset=utf-8")


# ============================================
# API de Asignación
# ============================================

@app.post("/api/ronda/ejecutar")
async def ejecutar_asignacion(
    archivo_oferta: UploadFile = File(...),
    archivo_postulaciones: UploadFile = File(...),
    anio: int = Form(...),
    semestre: int = Form(..., ge=1, le=2),
    observaciones: Optional[str] = Form(None)
):
    """Ejecuta una nueva ronda de asignación de cupos."""
    try:
        print(f"=== INICIANDO ASIGNACIÓN ===")
        print(f"Período: {anio}-{semestre}")
        print(f"Archivo oferta: {archivo_oferta.filename}")
        print(f"Archivo postulaciones: {archivo_postulaciones.filename}")
        
        periodo = PeriodoAcademico(anio=anio, semestre=Semestre(semestre))
        
        # Guardar archivos temporalmente
        os.makedirs(TEMP_DIR, exist_ok=True)
        ruta_oferta = TEMP_DIR / f"oferta_{anio}_{semestre}.csv"
        ruta_postulaciones = TEMP_DIR / f"postulaciones_{anio}_{semestre}.csv"
        
        print(f"Guardando archivo oferta en: {ruta_oferta}")
        with open(ruta_oferta, "wb") as f:
            content = await archivo_oferta.read()
            f.write(content)
        
        print(f"Guardando archivo postulaciones en: {ruta_postulaciones}")
        with open(ruta_postulaciones, "wb") as f:
            content = await archivo_postulaciones.read()
            f.write(content)
        
        print("Archivos guardados. Creando contenedor...")
        container = Container()
        
        print("Obteniendo motor...")
        motor = container.motor()
        
        print("Ejecutando ronda...")
        ronda, resultados = motor.ejecutar_ronda(
            periodo=periodo,
            archivo_oferta=str(ruta_oferta),
            archivo_postulaciones=str(ruta_postulaciones),
            observaciones=observaciones
        )
        
        print(f"Ronda completada: {ronda.numero}")
        print(f"Total aspirantes: {ronda.total_aspirantes}")
        print(f"Total asignados: {ronda.total_asignados}")
        
        # Limpiar archivos temporales
        if ruta_oferta.exists():
            os.remove(ruta_oferta)
        if ruta_postulaciones.exists():
            os.remove(ruta_postulaciones)
        
        return {
            "success": True,
            "mensaje": f"Ronda {ronda.numero} del período {periodo} ejecutada exitosamente",
            "ronda": ronda.to_dict()
        }
        
    except Exception as e:
        print(f"=== ERROR EN ASIGNACIÓN ===")
        print(f"Error: {str(e)}")
        print(f"Traceback completo:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rondas/historial")
async def obtener_historial(
    anio: Optional[int] = None,
    semestre: Optional[int] = None
):
    """Obtiene el historial de rondas de asignación."""
    try:
        container = Container()
        motor = container.motor()
        
        # Obtener todas las rondas primero
        rondas = motor.obtener_historial_rondas(None)
        
        # Aplicar filtros
        filtro_aplicado = "Todos"
        if anio and semestre:
            rondas = [r for r in rondas if r.periodo.anio == anio and r.periodo.semestre.value == semestre]
            filtro_aplicado = f"{anio}-{semestre}"
        elif anio:
            rondas = [r for r in rondas if r.periodo.anio == anio]
            filtro_aplicado = f"Año {anio}"
        elif semestre:
            rondas = [r for r in rondas if r.periodo.semestre.value == semestre]
            filtro_aplicado = f"Semestre {semestre}"
        
        return {
            "total_rondas": len(rondas),
            "filtro_periodo": filtro_aplicado,
            "rondas": [r.to_dict() for r in rondas]
        }
        
    except Exception as e:
        print(f"Error en historial: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/periodos")
async def obtener_periodos():
    """Obtiene lista de períodos académicos con rondas registradas."""
    try:
        container = Container()
        motor = container.motor()
        periodos = motor.obtener_periodos()
        
        return {
            "total_periodos": len(periodos),
            "periodos": [
                {
                    "periodo_str": str(p),
                    "anio": p.anio,
                    "semestre": p.semestre.value
                } 
                for p in periodos
            ]
        }
        
    except Exception as e:
        print(f"Error en periodos: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/periodo/{anio}/{semestre}")
async def obtener_resumen_periodo(anio: int, semestre: int):
    """Obtiene resumen estadístico de un período específico."""
    try:
        motor = container.motor()
        periodo = PeriodoAcademico(anio=anio, semestre=Semestre(semestre))
        
        return JSONResponse(content=motor.obtener_resumen_periodo(periodo))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ronda/{anio}/{semestre}/{numero}")
async def obtener_ronda(anio: int, semestre: int, numero: int):
    """Obtiene información detallada de una ronda específica."""
    try:
        motor = container.motor()
        periodo = PeriodoAcademico(anio=anio, semestre=Semestre(semestre))
        
        ronda = motor.obtener_ronda(periodo, numero)
        
        if not ronda:
            raise HTTPException(
                status_code=404, 
                detail=f"Ronda {numero} del período {periodo} no encontrada"
            )
        
        return JSONResponse(content=ronda.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ronda/{anio}/{semestre}/{numero}/descargar/{tipo}")
async def descargar_archivo_ronda(
    anio: int, 
    semestre: int, 
    numero: int, 
    tipo: str
):
    """
    Descarga un archivo de una ronda específica.
    
    - tipo: 'oferta', 'postulaciones' o 'resultados'
    """
    try:
        if tipo not in ["oferta", "postulaciones", "resultados"]:
            raise HTTPException(
                status_code=400, 
                detail="Tipo debe ser: oferta, postulaciones o resultados"
            )
        
        gestor = container.gestor_rondas()
        periodo = PeriodoAcademico(anio=anio, semestre=Semestre(semestre))
        
        ronda = gestor.obtener_ronda(periodo, numero)
        
        if not ronda:
            raise HTTPException(
                status_code=404, 
                detail=f"Ronda {numero} del período {periodo} no encontrada"
            )
        
        ruta = gestor.obtener_ruta_archivo(ronda, tipo)
        
        if not os.path.exists(ruta):
            raise HTTPException(
                status_code=404, 
                detail=f"Archivo de {tipo} no encontrado"
            )
        
        # Determinar nombre del archivo para descarga
        nombres = {
            "oferta": ronda.archivo_oferta,
            "postulaciones": ronda.archivo_postulaciones,
            "resultados": ronda.archivo_resultados
        }
        
        return FileResponse(
            ruta,
            media_type="text/csv",
            filename=nombres[tipo]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ronda/{anio}/{semestre}/{numero}")
async def eliminar_ronda(anio: int, semestre: int, numero: int):
    """Elimina una ronda específica y sus archivos asociados."""
    try:
        gestor = container.gestor_rondas()
        periodo = PeriodoAcademico(anio=anio, semestre=Semestre(semestre))
        
        eliminado = gestor.eliminar_ronda(periodo, numero)
        
        if not eliminado:
            raise HTTPException(
                status_code=404, 
                detail=f"Ronda {numero} del período {periodo} no encontrada"
            )
        
        return JSONResponse(content={
            "success": True,
            "mensaje": f"Ronda {numero} del período {periodo} eliminada correctamente"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS LEGACY (para compatibilidad)
# ============================================================================

@app.get("/api/oferta")
def get_oferta():
    """Devuelve la oferta académica (lista de carreras)."""
    lector = container.lector_datos()
    aspirantes, carreras = lector.cargar_datos()
    # serializar carreras
    data = [c.__dict__ for c in carreras]
    return JSONResponse(content={"oferta": data})


@app.get("/api/postulaciones")
def get_postulaciones():
    lector = container.lector_datos()
    aspirantes, carreras = lector.cargar_datos()
    data = [a.__dict__ for a in aspirantes]
    return JSONResponse(content={"aspirantes": data})


@app.get("/api/debug")
def api_debug():
    """Endpoint de depuración: devuelve config.json, rutas y lista de archivos en inputs/ y outputs/."""
    resp = {}
    try:
        # Config loaded by container
        cfg = None
        try:
            cfg = container.config()
        except Exception:
            # container.config may be provider; try reading file
            import json as _json
            try:
                with open('config.json', 'r', encoding='utf-8') as f:
                    cfg = _json.load(f)
            except Exception:
                cfg = None

        resp['config'] = cfg

        # Normativa routes
        try:
            normativa = container.normativa()
            resp['rutas'] = normativa.rutas
        except Exception:
            resp['rutas'] = None

        # List files in inputs and outputs
        inputs_list = []
        outputs_list = []
        try:
            if os.path.isdir('inputs'):
                inputs_list = os.listdir('inputs')
            if os.path.isdir('outputs'):
                outputs_list = os.listdir('outputs')
        except Exception as e:
            resp['list_error'] = str(e)

        resp['inputs'] = inputs_list
        resp['outputs'] = outputs_list

        return JSONResponse(content={'debug': resp})

    except Exception as e:
        return JSONResponse(content={'error': str(e)}, status_code=500)


@app.post("/api/upload")
async def upload_files(oferta: UploadFile | None = File(None), postulaciones: UploadFile | None = File(None)):
    """Permite subir archivos CSV para oferta y matriz de postulaciones.
    Se escriben en las rutas definidas en config.json.
    Retorna JSON con {'saved': {...}} o {'error': 'mensaje'} y códigos adecuados.
    """
    normativa = container.normativa()
    rutas = normativa.rutas

    saved = {}
    try:
        if oferta is not None and rutas.get('oferta_academica'):
            dest = rutas['oferta_academica']
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            content = await oferta.read()
            with open(dest, 'wb') as f:
                f.write(content)
            saved['oferta_academica'] = dest

        if postulaciones is not None and rutas.get('matriz_postulaciones'):
            dest = rutas['matriz_postulaciones']
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            content = await postulaciones.read()
            with open(dest, 'wb') as f:
                f.write(content)
            saved['matriz_postulaciones'] = dest

        # Siempre devolver un JSON claro
        return JSONResponse(content={"saved": saved}, status_code=200)

    except Exception as e:
        msg = f"Error guardando archivos: {e}"
        print(msg)
        normativa.reportar_incidencia(msg)
        return JSONResponse(content={"error": msg}, status_code=500)


def _run_motor_task():
    try:
        motor = container.motor()
        motor.ejecutar_proceso()
    except Exception as e:
        # motor prints its own errors; swallow to avoid crashing the background task
        print(f"Error al ejecutar motor en background: {e}")


@app.post("/api/ejecutar")
def ejecutar(background_tasks: BackgroundTasks):
    """Dispara el motor de asignación en background y responde inmediatamente (modo legacy)."""
    background_tasks.add_task(_run_motor_task)
    return JSONResponse(content={"status": "started"})


@app.get("/api/resultados")
def resultados():
    normativa = container.normativa()
    ruta = normativa.rutas.get('resultados_asignacion')
    if ruta and os.path.isfile(ruta):
        # devolver CSV como archivo descargable
        return FileResponse(path=ruta, media_type='text/csv', filename=os.path.basename(ruta))
    return JSONResponse(content={"error": "Archivo de resultados no encontrado."}, status_code=404)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main_fastapi:app', host='127.0.0.1', port=8000, reload=True)
