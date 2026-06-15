import cv2
import yaml
import os
import logging
from app.core.copia_system import CopIASystem

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s"
)

def main():
    # Cargar config
    config_path = "config/copia_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    camera_index = config.get("camera_index", 0)
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara {camera_index}")
        return

    system = CopIASystem(config_path)
    print("[INFO] CopIA System Inicializado. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Procesar frame
        processed_frame, log_data = system.process_frame(frame)
        
        # Dibujar UI en pantalla
        if log_data:
            draw_ui(processed_frame, log_data, system.profile.get("initialized", False), system.calibrator.progress())

        cv2.imshow("CopIA - Driver Monitoring System", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    system.shutdown()
    cap.release()
    cv2.destroyAllWindows()

def draw_ui(frame, data, profile_ready, calib_progress):
    color_text = (255, 255, 255)
    
    # Colores según riesgo
    risk = data["risk_score"]
    if risk < 30:
        risk_color = (0, 255, 0) # Verde
    elif risk < 55:
        risk_color = (0, 255, 255) # Amarillo
    elif risk < 75:
        risk_color = (0, 165, 255) # Naranja
    else:
        risk_color = (0, 0, 255) # Rojo

    y = 40
    cv2.putText(frame, f"EAR: {data['ear']:.3f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"MAR: {data['mar']:.3f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"PERCLOS: {data['perclos']*100:.2f}%", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"PITCH: {data['pitch']:.1f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    y += 30
    cv2.putText(frame, f"Eye Prob: {data['eye_closed_prob']:.2f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)
    
    # Barra de Riesgo
    y += 40
    bar_y = y
    cv2.rectangle(frame, (20, bar_y), (220, bar_y + 30), (50, 50, 50), -1)
    cv2.rectangle(frame, (20, bar_y), (20 + int(risk * 2), bar_y + 30), risk_color, -1)
    cv2.putText(frame, f"RISK: {risk:.1f}", (230, bar_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.8, risk_color, 2)
    
    y = bar_y + 60
    cv2.putText(frame, f"LEVEL: {data['alert_level']}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, risk_color, 2)
    y += 30
    cv2.putText(frame, f"EVENT: {data['event_type'].upper()}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_text, 2)
    
    # Explicación
    cv2.putText(frame, f"MSG: {data['explanation']}", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    if not profile_ready:
        prog = int(calib_progress * 100)
        cv2.putText(frame, f"CALIBRANDO: {prog}%", (frame.shape[1] - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

if __name__ == "__main__":
    main()