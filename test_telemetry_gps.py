import requests
import time
import math
import random

# Reemplaza esto con el ID de un conductor existente en tu BD
CONDUCTOR_ID = 1

def simular_movimiento(lat_inicio, lng_inicio, lat_fin, lng_fin, pasos=100):
    for i in range(pasos):
        t = i / float(pasos)
        
        # Interpolar coordenadas
        lat_actual = lat_inicio + (lat_fin - lat_inicio) * t
        lng_actual = lng_inicio + (lng_fin - lng_inicio) * t
        
        # Simular variaciones de fatiga
        ear = 0.30 - (random.random() * 0.1 if i % 10 == 0 else random.random() * 0.05)
        riesgo = 0
        tipo_evento = "normal"
        alert_level = 0
        
        if ear < 0.20:
            riesgo = 80
            tipo_evento = "somnolencia"
            alert_level = 2
            
        payload = {
            "conductor_id": CONDUCTOR_ID,
            "lat": lat_actual,
            "lng": lng_actual,
            "log_data": {
                "ear": ear,
                "mar": 0.1,
                "pitch": 0.0,
                "yaw": 0.0,
                "perclos": 0.05 if ear > 0.20 else 0.25,
                "risk_score": riesgo,
                "event_type": tipo_evento,
                "alert_level": alert_level,
                "explanation": "Simulación GPS en movimiento"
            }
        }
        
        try:
            res = requests.post("http://localhost:8000/api/telemetry", json=payload)
            print(f"Paso {i}: Lat {lat_actual:.5f}, Lng {lng_actual:.5f} | Estado: {res.status_code}")
        except Exception as e:
            print("Error conectando al servidor:", e)
            
        time.sleep(1) # Enviar cada 1 segundo

if __name__ == "__main__":
    print("Iniciando simulación de GPS de camión...")
    # Coordenadas de ejemplo (ej. Lima a alguna parte)
    LAT_INICIAL = -12.046374
    LNG_INICIAL = -77.042793
    
    LAT_FINAL = -12.060000
    LNG_FINAL = -77.050000
    
    simular_movimiento(LAT_INICIAL, LNG_INICIAL, LAT_FINAL, LNG_FINAL)
