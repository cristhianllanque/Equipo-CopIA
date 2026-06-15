import pytest
from app.ai.driver_profile import DriverProfileManager
from app.models.db_models import Base, Conductor, PerfilCalibracion
from app.core.database import engine, SessionLocal

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Inicializa las tablas si no existen
    Base.metadata.create_all(bind=engine)
    yield
    # No droppeamos la base de datos real, solo limpiamos los tests
    db = SessionLocal()
    db.query(PerfilCalibracion).filter(PerfilCalibracion.conductor_id == 999).delete()
    db.query(Conductor).filter(Conductor.id == 999).delete()
    db.commit()
    db.close()

def test_driver_profile_lifecycle():
    manager = DriverProfileManager(conductor_id=999)
    
    # Test load empty
    profile = manager.load_profile()
    assert profile["initialized"] == False
    
    # Test calibration
    calib_data = {
        "ear_baseline": 0.25,
        "mar_baseline": 0.35,
        "pitch_baseline": 1.0,
        "normal_frames_observed": 100
    }
    profile = manager.initialize_from_calibration(profile, calib_data)
    assert profile["initialized"] == True
    assert profile["ear_baseline"] == 0.25
    
    # Test update
    profile = manager.update_online(profile, ear=0.15, mar=0.35, pitch=1.0)
    assert profile["ear_baseline"] < 0.25 # Ha bajado por el suavizado (alpha=0.005)
