import os
import time
from app.core.database import SessionLocal
from app.models.db_models import Conductor, PerfilCalibracion, SesionConduccion
from datetime import datetime

class DriverProfileManager:
    def __init__(self, conductor_id=1):
        self.conductor_id = conductor_id
        self._ensure_conductor_exists()

    def _ensure_conductor_exists(self):
        db = SessionLocal()
        try:
            conductor = db.query(Conductor).filter(Conductor.id == self.conductor_id).first()
            if not conductor:
                conductor = Conductor(id=self.conductor_id, nombre="Conductor Predeterminado")
                db.add(conductor)
                db.commit()
        finally:
            db.close()

    def load_profile(self):
        db = SessionLocal()
        try:
            perfil = db.query(PerfilCalibracion).filter(PerfilCalibracion.conductor_id == self.conductor_id).first()
            if not perfil or not perfil.initialized:
                # Retornamos dict para retrocompatibilidad
                return {"initialized": False}
            
            return {
                "initialized": perfil.initialized,
                "ear_baseline": perfil.ear_baseline,
                "mar_baseline": perfil.mar_baseline,
                "pitch_baseline": perfil.pitch_baseline,
                "yaw_baseline": perfil.yaw_baseline,
                "normal_frames_observed": perfil.normal_frames_observed
            }
        finally:
            db.close()

    def save_profile(self, profile):
        db = SessionLocal()
        try:
            perfil = db.query(PerfilCalibracion).filter(PerfilCalibracion.conductor_id == self.conductor_id).first()
            if not perfil:
                perfil = PerfilCalibracion(conductor_id=self.conductor_id)
                db.add(perfil)
            
            perfil.initialized = profile.get("initialized", False)
            perfil.ear_baseline = profile.get("ear_baseline", 0.28)
            perfil.mar_baseline = profile.get("mar_baseline", 0.30)
            perfil.pitch_baseline = profile.get("pitch_baseline", 0.0)
            perfil.yaw_baseline = profile.get("yaw_baseline", 0.0)
            perfil.normal_frames_observed = profile.get("normal_frames_observed", 0)
            perfil.last_update = datetime.utcnow()
            
            db.commit()
        finally:
            db.close()

    def initialize_from_calibration(self, profile, calib_data):
        profile.update({
            "initialized": True,
            "ear_baseline": calib_data.get("ear_baseline", 0.28),
            "mar_baseline": calib_data.get("mar_baseline", 0.30),
            "pitch_baseline": calib_data.get("pitch_baseline", 0.0),
            "yaw_baseline": 0.0,
            "normal_frames_observed": calib_data.get("normal_frames_observed", 0),
        })
        self.save_profile(profile)
        return profile

    def update_online(self, profile, ear, mar, pitch):
        alpha = 0.005
        profile["ear_baseline"] = (1 - alpha) * profile.get("ear_baseline", 0.28) + alpha * ear
        profile["mar_baseline"] = (1 - alpha) * profile.get("mar_baseline", 0.3) + alpha * mar
        profile["pitch_baseline"] = (1 - alpha) * profile.get("pitch_baseline", 0) + alpha * pitch
        self.save_profile(profile)
        return profile