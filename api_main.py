import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import hashlib
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s"
)

# Base de datos local en memoria (caché) para la telemetría en tiempo real
# Formato: { conductor_id: { "log_data": {...}, "snapshot_b64": "...", "last_seen": timestamp } }
fleet_status = {}

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading
    threading.Thread(target=sync_firebase_gps, daemon=True).start()
    logging.info("Sincronizador de Firebase GPS iniciado en segundo plano.")
    yield

app = FastAPI(title="CopIA Cloud Server", description="Servidor central para recepción de telemetría IoT", version="2.0.0", lifespan=lifespan)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>CopIA Cloud Server</title>
            <style>
                body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #1e1e1e; color: #fff; }
                h1 { color: #0ea5e9; }
                a { color: #0ea5e9; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Transportes Veloz - CopIA Cloud API</h1>
            <p>Servidor central recibiendo telemetría de la flota.</p>
            <p><a href="/docs" target="_blank">Ver Documentación de la API (Swagger)</a></p>
        </body>
    </html>
    """

from app.core.database import SessionLocal
from app.models.db_models import Conductor, SesionConduccion, EventoFatiga

# --- MODELOS PYDANTIC ---
class ConductorCreate(BaseModel):
    nombre: str
    username: str
    password: str
    vehiculo: str
    ruta_asignada: str = None
    foto_url: str = None
    vehiculo_foto_url: str = None

class RutaCreate(BaseModel):
    origen: str
    destino: str

class StartTripPayload(BaseModel):
    conductor_id: int
    ruta_id: int

class AuthLogin(BaseModel):
    username: str
    password: str

class TelemetryPayload(BaseModel):
    conductor_id: int
    log_data: dict
    lat: float = None
    lng: float = None
    snapshot_b64: str = None  # Imagen JPG en base64

class EndTripPayload(BaseModel):
    conductor_id: int

class PanicPayload(BaseModel):
    conductor_id: int
    lat: float = None
    lng: float = None

class PerfilUpdate(BaseModel):
    conductor_id: int
    ear_baseline: float = None
    mar_baseline: float = None
    pitch_baseline: float = None
    yaw_baseline: float = None

# --- ENDPOINTS GESTIÓN DE FLOTA ---

@app.get("/api/conductores")
def get_conductores():
    db = SessionLocal()
    try:
        conductores = db.query(Conductor).all()
        return [{
            "id": c.id, 
            "nombre": c.nombre, 
            "username": c.username,
            "vehiculo": c.vehiculo,
            "ruta_asignada": c.ruta_asignada,
            "foto_url": c.foto_url,
            "vehiculo_foto_url": c.vehiculo_foto_url,
            "estado": c.estado,
            "fecha_registro": c.fecha_registro.isoformat()
        } for c in conductores]
    finally:
        db.close()

@app.post("/api/conductores")
def create_conductor(data: ConductorCreate):
    db = SessionLocal()
    try:
        pw_hash = hashlib.sha256(data.password.encode()).hexdigest()
        new_driver = Conductor(
            nombre=data.nombre,
            username=data.username,
            password_hash=pw_hash,
            vehiculo=data.vehiculo,
            ruta_asignada=data.ruta_asignada,
            foto_url=data.foto_url,
            vehiculo_foto_url=data.vehiculo_foto_url
        )
        db.add(new_driver)
        db.commit()
        db.refresh(new_driver)
        return {"id": new_driver.id, "nombre": new_driver.nombre, "status": "created"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=400, content={"error": str(e)})
    finally:
        db.close()

@app.post("/api/auth/conductor")
def auth_conductor(data: AuthLogin):
    db = SessionLocal()
    try:
        driver = db.query(Conductor).filter(Conductor.username == data.username).first()
        if not driver:
            return JSONResponse(status_code=401, content={"error": "Credenciales inválidas"})
        
        pw_hash = hashlib.sha256(data.password.encode()).hexdigest()
        if driver.password_hash != pw_hash:
            return JSONResponse(status_code=401, content={"error": "Credenciales inválidas"})

        return {
            "success": True, 
            "conductor_id": driver.id, 
            "nombre": driver.nombre,
            "vehiculo": driver.vehiculo
        }
    finally:
        db.close()

@app.post("/api/trip/start")
def start_trip(data: StartTripPayload):
    db = SessionLocal()
    try:
        sesion = SesionConduccion(
            conductor_id=data.conductor_id,
            ruta_id=data.ruta_id,
            inicio_sesion=datetime.utcnow()
        )
        db.add(sesion)
        db.commit()
        return {"success": True, "sesion_id": sesion.id}
    finally:
        db.close()

@app.post("/api/trip/end")
def end_trip(data: EndTripPayload):
    db = SessionLocal()
    try:
        # Encontrar la sesión activa del conductor
        sesion = db.query(SesionConduccion).filter(
            SesionConduccion.conductor_id == data.conductor_id,
            SesionConduccion.fin_sesion == None
        ).order_by(SesionConduccion.id.desc()).first()
        
        if not sesion:
            return JSONResponse(status_code=400, content={"error": "No hay sesión activa para este conductor"})
        
        sesion.fin_sesion = datetime.utcnow()
        
        # Calcular eventos
        eventos = db.query(EventoFatiga).filter(EventoFatiga.sesion_id == sesion.id).all()
        total_eventos = len(eventos)
        avg_risk = sum([e.nivel_riesgo for e in eventos]) / total_eventos if total_eventos > 0 else 0
        
        db.commit()
        return {
            "success": True, 
            "sesion_id": sesion.id, 
            "total_eventos": total_eventos, 
            "riesgo_promedio": round(avg_risk, 2)
        }
    finally:
        db.close()

@app.post("/api/trip/panic")
def panic_alert(data: PanicPayload):
    db = SessionLocal()
    try:
        sesion = db.query(SesionConduccion).filter(
            SesionConduccion.conductor_id == data.conductor_id,
            SesionConduccion.fin_sesion == None
        ).order_by(SesionConduccion.id.desc()).first()
        
        if sesion:
            evento = EventoFatiga(
                sesion_id=sesion.id,
                tipo_evento="ROBO_ASALTO",
                nivel_riesgo=100,
                timestamp=datetime.utcnow()
            )
            db.add(evento)
            db.commit()
            return {"success": True, "message": "Alerta de pánico registrada."}
        return JSONResponse(status_code=400, content={"error": "No hay sesión activa para el botón de pánico"})
    finally:
        db.close()

from app.models.db_models import Ruta

@app.get("/api/rutas")
def get_rutas():
    db = SessionLocal()
    try:
        rutas = db.query(Ruta).all()
        return [{"id": r.id, "origen": r.origen, "destino": r.destino, "estado": r.estado} for r in rutas]
    finally:
        db.close()

@app.post("/api/rutas")
def create_ruta(data: RutaCreate):
    db = SessionLocal()
    try:
        nueva_ruta = Ruta(origen=data.origen, destino=data.destino)
        db.add(nueva_ruta)
        db.commit()
        db.refresh(nueva_ruta)
        return {"id": nueva_ruta.id, "origen": nueva_ruta.origen, "destino": nueva_ruta.destino}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=400, content={"error": str(e)})
    finally:
        db.close()

# --- ENDPOINTS TELEMETRÍA (IoT Edge) ---

@app.post("/api/telemetry")
def receive_telemetry(payload: TelemetryPayload):
    """
    Recibe la telemetría enviada por la Raspberry Pi del camión.
    """
    global fleet_status
    cid = payload.conductor_id
    
    fleet_status[cid] = {
        "log_data": payload.log_data,
        "lat": payload.lat,
        "lng": payload.lng,
        "snapshot_b64": payload.snapshot_b64,
        "last_seen": datetime.utcnow().isoformat()
    }

    # Si hay un evento crítico, lo guardamos en la base de datos central
    if payload.log_data.get("alert_level", 0) > 0:
        db = SessionLocal()
        try:
            # Buscamos la última sesión activa del conductor
            sesion = db.query(SesionConduccion).filter(
                SesionConduccion.conductor_id == cid, 
                SesionConduccion.fin_sesion == None
            ).order_by(SesionConduccion.id.desc()).first()
            
            if sesion:
                evento = EventoFatiga(
                    sesion_id=sesion.id,
                    tipo_evento=payload.log_data.get("event_type", "alerta"),
                    nivel_riesgo=payload.log_data.get("risk_score", 0),
                    ear_registrado=payload.log_data.get("ear", 0),
                    mar_registrado=payload.log_data.get("mar", 0)
                )
                db.add(evento)
                db.commit()
        finally:
            db.close()

    return {"status": "ok"}

@app.get("/api/status")
def get_status(conductor_id: int = Query(None)):
    """
    El Dashboard consulta este endpoint para leer la telemetría en vivo de un conductor.
    """
    global fleet_status
    if conductor_id is None:
        return JSONResponse(status_code=400, content={"error": "Falta conductor_id"})
    
    status = fleet_status.get(conductor_id, None)
    if not status:
        return JSONResponse(content={"offline": True})
    
    # Inyectar lat/lng dentro de log_data para compatibilidad fácil en el frontend
    status_no_img = {k: v for k, v in status.items() if k != "snapshot_b64"}
    if "log_data" in status_no_img:
        status_no_img["log_data"]["lat"] = status_no_img.get("lat")
        status_no_img["log_data"]["lng"] = status_no_img.get("lng")

    return JSONResponse(content=status_no_img)

import asyncio
from fastapi.responses import StreamingResponse
import base64

async def generate_mjpeg_stream(conductor_id: int):
    global fleet_status
    last_b64 = None
    while True:
        status = fleet_status.get(conductor_id)
        if status and status.get("snapshot_b64"):
            # Enviar el frame solo si es diferente al anterior (nuevo snapshot)
            if status["snapshot_b64"] != last_b64:
                last_b64 = status["snapshot_b64"]
                try:
                    frame_bytes = base64.b64decode(last_b64)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                except:
                    pass
        await asyncio.sleep(0.03)

@app.get("/api/video_feed")
def video_feed(conductor_id: int = Query(...)):
    return StreamingResponse(generate_mjpeg_stream(conductor_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/eventos")
def get_eventos(conductor_id: int = Query(None)):
    db = SessionLocal()
    try:
        query = db.query(EventoFatiga).join(SesionConduccion)
        if conductor_id:
            query = query.filter(SesionConduccion.conductor_id == conductor_id)
            
        eventos = query.order_by(EventoFatiga.timestamp.desc()).limit(50).all()
        return [{
            "id": e.id,
            "sesion_id": e.sesion_id,
            "timestamp": e.timestamp.isoformat(),
            "tipo_evento": e.tipo_evento,
            "nivel_riesgo": e.nivel_riesgo,
            "ear_registrado": e.ear_registrado,
            "mar_registrado": e.mar_registrado
        } for e in eventos]
    finally:
        db.close()

from sqlalchemy import func

@app.get("/api/analytics")
def get_analytics():
    db = SessionLocal()
    try:
        # Riesgo promedio por conductor
        conductor_riesgo = db.query(
            Conductor.nombre,
            func.count(EventoFatiga.id).label("total_eventos"),
            func.avg(EventoFatiga.nivel_riesgo).label("riesgo_promedio")
        ).join(SesionConduccion, Conductor.id == SesionConduccion.conductor_id)\
         .join(EventoFatiga, SesionConduccion.id == EventoFatiga.sesion_id)\
         .group_by(Conductor.id).all()

        ranking_conductores = [{
            "nombre": c.nombre,
            "total_eventos": c.total_eventos,
            "riesgo_promedio": round(c.riesgo_promedio, 2) if c.riesgo_promedio else 0
        } for c in conductor_riesgo]

        # Total de eventos hoy
        hoy = datetime.utcnow().date()
        total_hoy = db.query(EventoFatiga).filter(func.date(EventoFatiga.timestamp) == hoy).count()

        return {
            "ranking_conductores": ranking_conductores,
            "total_eventos_hoy": total_hoy
        }
    finally:
        db.close()

from app.models.db_models import PerfilCalibracion

@app.get("/api/config/perfil")
def get_perfil(conductor_id: int = Query(...)):
    db = SessionLocal()
    try:
        perfil = db.query(PerfilCalibracion).filter(PerfilCalibracion.conductor_id == conductor_id).first()
        if not perfil:
            return JSONResponse(status_code=404, content={"error": "Perfil no encontrado"})
        return {
            "ear_baseline": perfil.ear_baseline,
            "mar_baseline": perfil.mar_baseline,
            "pitch_baseline": perfil.pitch_baseline,
            "yaw_baseline": perfil.yaw_baseline,
            "initialized": perfil.initialized
        }
    finally:
        db.close()

@app.post("/api/config/perfil")
def update_perfil(data: PerfilUpdate):
    db = SessionLocal()
    try:
        perfil = db.query(PerfilCalibracion).filter(PerfilCalibracion.conductor_id == data.conductor_id).first()
        if not perfil:
            perfil = PerfilCalibracion(conductor_id=data.conductor_id)
            db.add(perfil)
        
        if data.ear_baseline is not None: perfil.ear_baseline = data.ear_baseline
        if data.mar_baseline is not None: perfil.mar_baseline = data.mar_baseline
        if data.pitch_baseline is not None: perfil.pitch_baseline = data.pitch_baseline
        if data.yaw_baseline is not None: perfil.yaw_baseline = data.yaw_baseline
        
        perfil.initialized = True
        db.commit()
        return {"success": True, "message": "Perfil actualizado correctamente"}
    finally:
        db.close()

import requests
import threading
import time

def sync_firebase_gps():
    """ Tarea en segundo plano para sincronizar GPS desde Firebase """
    global fleet_status
    while True:
        try:
            res = requests.get("https://webveloz-gps-default-rtdb.firebaseio.com/vehiculos.json", timeout=15)
            if res.status_code == 200 and res.json():
                vehiculos_fb = res.json()
                
                db = SessionLocal()
                try:
                    # Traemos todos los conductores para emparejar su vehiculo
                    conductores = db.query(Conductor).all()
                    
                    for c in conductores:
                        if c.vehiculo and c.vehiculo in vehiculos_fb:
                            fb_data = vehiculos_fb[c.vehiculo]
                            lat = fb_data.get("lat")
                            lng = fb_data.get("lng")
                            velocidad = fb_data.get("velocidad", 0)
                            
                            if c.id in fleet_status:
                                fleet_status[c.id]["lat"] = lat
                                fleet_status[c.id]["lng"] = lng
                                if not fleet_status[c.id].get("log_data"):
                                    fleet_status[c.id]["log_data"] = {}
                                fleet_status[c.id]["log_data"]["velocidad"] = velocidad
                            else:
                                fleet_status[c.id] = {
                                    "log_data": {"velocidad": velocidad, "ear": 0, "mar": 0, "pitch": 0, "risk_score": 0},
                                    "lat": lat,
                                    "lng": lng,
                                    "snapshot_b64": None,
                                    "last_seen": datetime.utcnow().isoformat()
                                }
                finally:
                    db.close()
        except requests.exceptions.Timeout:
            logging.warning("Sincronizador de Firebase GPS: Tiempo de espera agotado (timeout). Reintentando en breve...")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error de red sincronizando con Firebase: {e}")
        except Exception as e:
            logging.error(f"Error inesperado sincronizando con Firebase: {e}")
            
        time.sleep(3)  # Consultar cada 3 segundos



if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=False)
