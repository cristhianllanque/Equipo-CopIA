import cv2
import yaml
import os
import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.copia_system import CopIASystem
import uvicorn
from contextlib import asynccontextmanager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s"
)

# Variables globales para el estado
system = None
cap = None
latest_log_data = {
    "risk_score": 0, "alert_level": 0, "event_type": "normal",
    "explanation": "Iniciando...", "ear": 0, "mar": 0, "perclos": 0, "pitch": 0,
    "eye_closed_prob": 0
}
latest_frame_jpg = None
is_running = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global system, cap, is_running
    config_path = "config/copia_config.yaml"
    
    system = CopIASystem(config_path)
    config = system.config
    
    camera_index = config.get("camera_index", 0)
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        logging.error(f"No se pudo abrir la cámara {camera_index}")
    else:
        logging.info("Cámara y CopIASystem inicializados correctamente.")
        is_running = True
        
    yield
    
    is_running = False
    if system:
        system.shutdown()
    if cap:
        cap.release()
    logging.info("Sistema apagado de forma segura.")

app = FastAPI(title="CopIA API", description="API para el sistema de asistencia CopIA", version="1.0.0", lifespan=lifespan)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def draw_ui(frame, data, profile_ready, calib_progress):
    color_text = (255, 255, 255)
    
    # Colores según riesgo
    risk = data.get("risk_score", 0)
    if risk < 30:
        risk_color = (0, 255, 0) # Verde
    elif risk < 55:
        risk_color = (0, 255, 255) # Amarillo
    elif risk < 75:
        risk_color = (0, 165, 255) # Naranja
    else:
        risk_color = (0, 0, 255) # Rojo

    y = 40
    cv2.putText(frame, f"EAR: {data.get('ear', 0):.3f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"MAR: {data.get('mar', 0):.3f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"PERCLOS: {data.get('perclos', 0)*100:.2f}%", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"PITCH: {data.get('pitch', 0):.1f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    
    # Barra de Riesgo
    y += 40
    bar_y = y
    cv2.rectangle(frame, (20, bar_y), (220, bar_y + 30), (50, 50, 50), -1)
    cv2.rectangle(frame, (20, bar_y), (20 + int(risk * 2), bar_y + 30), risk_color, -1)
    cv2.putText(frame, f"RISK: {risk:.1f}", (230, bar_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.8, risk_color, 2)
    
    y = bar_y + 60
    cv2.putText(frame, f"LEVEL: {data.get('alert_level', 0)}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, risk_color, 2)
    y += 30
    cv2.putText(frame, f"EVENT: {data.get('event_type', 'normal').upper()}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_text, 2)
    
    # Explicación
    cv2.putText(frame, f"MSG: {data.get('explanation', '')}", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    if not profile_ready:
        prog = int(calib_progress * 100)
        cv2.putText(frame, f"CALIBRANDO: {prog}%", (frame.shape[1] - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

async def generate_frames():
    global latest_log_data, latest_frame_jpg, is_running
    
    while is_running and cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            await asyncio.sleep(0.01)
            continue

        processed_frame, log_data = system.process_frame(frame)
        
        if log_data:
            latest_log_data = log_data
            draw_ui(processed_frame, log_data, system.profile.get("initialized", False), system.calibrator.progress())

        # Codificar a JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if ret:
            latest_frame_jpg = buffer.tobytes()
            # Formato multipart para stream de video
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame_jpg + b'\r\n')
        
        # Pequeño sleep para no bloquear el event loop por completo
        await asyncio.sleep(0.01)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>CopIA API</title>
            <style>
                body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #1e1e1e; color: #fff; }
                h1 { color: #4CAF50; }
                a { color: #4CAF50; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>CopIA AI Engine (Online)</h1>
            <p>El motor de Inteligencia Artificial está corriendo de fondo.</p>
            <p><a href="/docs" target="_blank">Ver Documentación de la API (Swagger)</a></p>
            <p><a href="/video_feed" target="_blank">Ver Stream de Cámara (Video en Vivo)</a></p>
            <p><a href="/api/status" target="_blank">Ver Estado (JSON en Vivo)</a></p>
            <p><a href="/api/profile" target="_blank">Ver Perfil Calibrado</a></p>
        </body>
    </html>
    """

from app.core.database import SessionLocal
from app.models.db_models import Conductor, SesionConduccion, EventoFatiga

@app.get("/api/status")
def get_status():
    global latest_log_data
    return JSONResponse(content=latest_log_data)

@app.get("/api/profile")
def get_profile():
    global system
    if system and system.profile:
        return JSONResponse(content=system.profile)
    return JSONResponse(content={"initialized": False})

@app.get("/api/conductores")
def get_conductores():
    db = SessionLocal()
    try:
        conductores = db.query(Conductor).all()
        return [{"id": c.id, "nombre": c.nombre, "fecha_registro": c.fecha_registro.isoformat()} for c in conductores]
    finally:
        db.close()

@app.get("/api/sesiones")
def get_sesiones():
    db = SessionLocal()
    try:
        sesiones = db.query(SesionConduccion).order_by(SesionConduccion.inicio_sesion.desc()).limit(20).all()
        return [{
            "id": s.id, 
            "conductor_id": s.conductor_id, 
            "inicio_sesion": s.inicio_sesion.isoformat() if s.inicio_sesion else None,
            "fin_sesion": s.fin_sesion.isoformat() if s.fin_sesion else None
        } for s in sesiones]
    finally:
        db.close()

@app.get("/api/eventos")
def get_eventos():
    db = SessionLocal()
    try:
        eventos = db.query(EventoFatiga).order_by(EventoFatiga.timestamp.desc()).limit(50).all()
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

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=False)
