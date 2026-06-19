import cv2
import json
import base64
import requests
import time
import getpass
import logging
import os
from dotenv import load_dotenv
import concurrent.futures
from app.core.copia_system import CopIASystem

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] CopIA Edge: %(message)s")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

def encode_image_base64(frame):
    # Aumentamos la resolución y calidad para que sea más nítido en el Dashboard
    small_frame = cv2.resize(frame, (640, 480))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
    ret, buffer = cv2.imencode('.jpg', small_frame, encode_param)
    if not ret:
        return None
    return base64.b64encode(buffer).decode('utf-8')

def authenticate():
    print("========================================")
    print("  CopIA Edge Client - Terminal de Cabina  ")
    print("========================================")
    username = input("Usuario: ")
    password = getpass.getpass("Contraseña: ")
    
    try:
        response = requests.post(f"{SERVER_URL}/api/auth/conductor", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                logging.info(f"Bienvenido {data['nombre']}. Sesión iniciada.")
                return data["conductor_id"], data["sesion_id"]
        else:
            logging.error("Credenciales inválidas o error en el servidor.")
            return None, None
    except requests.exceptions.ConnectionError:
        logging.error("No se pudo conectar con el servidor central.")
        return None, None

import threading

# Variable global para el último frame a enviar
latest_payload = None

def telemetry_sender_worker():
    global latest_payload
    while True:
        if latest_payload:
            payload = latest_payload
            latest_payload = None # Consumimos el payload
            try:
                # Usar sesión para mantener la conexión viva (mucho más rápido)
                with requests.Session() as s:
                    s.post(f"{SERVER_URL}/api/telemetry", json=payload, timeout=1.0)
            except Exception:
                pass
        else:
            time.sleep(0.01)

def run_edge_client(conductor_id, sesion_id):
    global latest_payload
    logging.info("Inicializando Motor de IA CopIA...")
    system = CopIASystem("config/copia_config.yaml", edge_mode=True)
    camera_index = system.config.get("camera_index", 1)
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logging.error("No se encontró ninguna cámara conectada a la Raspberry.")
        return

    logging.info("Cámara iniciada. Monitoreo en progreso...")
    
    # Iniciar hilo dedicado para envíos (sin encolar frames viejos)
    sender_thread = threading.Thread(target=telemetry_sender_worker, daemon=True)
    sender_thread.start()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            processed_frame, log_data = system.process_frame(frame)
            
            if log_data:
                # Actualizar el payload más reciente (sobrescribe si el hilo es lento, evitando lag)
                latest_payload = {
                    "conductor_id": conductor_id,
                    "log_data": log_data,
                    "snapshot_b64": encode_image_base64(processed_frame)
                }

            # Mostrar localmente (Pantalla de la Raspberry Pi)
            cv2.imshow("CopIA - Edge Monitor (Presiona 'q' para salir)", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logging.info("Deteniendo por orden del usuario.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        system.shutdown()

if __name__ == "__main__":
    cid, sid = authenticate()
    if cid is not None:
        run_edge_client(cid, sid)
