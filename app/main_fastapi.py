from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
import shutil
import os
import pandas as pd

app = FastAPI(title="SAU - API")

# Allow all origins for local dev (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar frontend estático en /static (carpeta web/ en la raíz del proyecto)
if os.path.isdir('web'):
    app.mount('/static', StaticFiles(directory='web'), name='static')


@app.get('/')
def root_index():
    """Sirve el index.html de la carpeta web/ en la raíz.
    Los assets (css/js) se sirven desde /static/* para evitar que
    las rutas POST a /api/* sean interceptadas por StaticFiles.
    """
    index_path = os.path.join('web', 'index.html')
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type='text/html')
    return JSONResponse(content={"error": "Front-end no encontrado."}, status_code=404)

container = Container()
# Forcing config load
try:
    container.config()
except Exception:
    pass


@app.get('/api/oferta')
def get_oferta():
    """Devuelve la oferta académica (lista de carreras)."""
    lector = container.lector_datos()
    aspirantes, carreras = lector.cargar_datos()
    # serializar carreras
    data = [c.__dict__ for c in carreras]
    return JSONResponse(content={"oferta": data})


@app.get('/api/postulaciones')
def get_postulaciones():
    lector = container.lector_datos()
    aspirantes, carreras = lector.cargar_datos()
    data = [a.__dict__ for a in aspirantes]
    return JSONResponse(content={"aspirantes": data})


@app.get('/api/debug')
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


@app.post('/api/upload')
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


@app.post('/api/ejecutar')
def ejecutar(background_tasks: BackgroundTasks):
    """Dispara el motor de asignación en background y responde inmediatamente."""
    background_tasks.add_task(_run_motor_task)
    return JSONResponse(content={"status": "started"})


@app.get('/api/resultados')
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
