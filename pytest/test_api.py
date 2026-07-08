import sys
import os
from fastapi.testclient import TestClient

# Asegurar que pytest puede importar los módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_main import app

client = TestClient(app)

def test_get_conductores():
    response = client.get("/api/conductores")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_eventos():
    response = client.get("/api/eventos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_auth_conductor_invalid():
    # Probar un intento de inicio de sesión inválido
    payload = {
        "username": "no_existe",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/conductor", json=payload)
    # Esperamos un 401 Unauthorized o 400 Bad Request
    assert response.status_code in [400, 401]

def test_rutas():
    response = client.get("/api/rutas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
