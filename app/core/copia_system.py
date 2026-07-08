import time
import os
import yaml
import logging
import csv
import numpy as np
import pygame
from datetime import datetime
import pytz

def get_peru_time():
    return datetime.now(pytz.timezone("America/Lima")).replace(tzinfo=None)

from app.core.frame_processor import FrameProcessor
from app.core.event_orchestrator import EventOrchestrator
from app.features.perclos import PerclosCalculator
from app.models.eye_state_classifier import EyeStateClassifier
from app.ai.risk_engine import ContinuousRiskEngine
from app.ai.temporal_memory import TemporalMemory
from app.ai.driver_profile import DriverProfileManager
from app.ai.baseline_calibrator import BaselineCalibrator
from app.alerts.yawn_detector import YawnDetector
from app.utils.temporal_smoother import TemporalSmoother

from app.core.database import SessionLocal
from app.models.db_models import SesionConduccion, EventoFatiga

logger = logging.getLogger("CopIA")

class CopIASystem:
    def __init__(self, config_path="config/copia_config.yaml", edge_mode=False):
        self.config = self._load_config(config_path)
        self.edge_mode = edge_mode
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            logger.warning("No se pudo inicializar pygame mixer.")

        self.eye_classifier = EyeStateClassifier() if self.config.get("use_eye_classifier", True) else None
        self.profile_manager = DriverProfileManager(edge_mode=self.edge_mode)
        self.profile = self.profile_manager.load_profile()
        self.calibrator = BaselineCalibrator(duration_seconds=12, min_samples=30)
        
        self.frame_processor = FrameProcessor(eye_classifier=self.eye_classifier)
        self.frame_processor.smoother = TemporalSmoother(window_size=15) 
        
        self.orchestrator = EventOrchestrator(config=self.config)
        self.risk_engine = ContinuousRiskEngine(self.profile, config=self.config)
        self.temporal_memory = TemporalMemory(window_seconds=10)
        self.perclos_calc = PerclosCalculator(window_seconds=60)
        
        self.eye_counter = 0
        self.pitch_counter = 0
        self.yaw_counter = 0
        self.yawn_detector = YawnDetector(mar_threshold=0.80, min_frames=15)
        
        self.start_time = time.time()
        self.last_perclos = 0.0

        # Logging de eventos a CSV y BD
        self._init_event_log()
        if not self.edge_mode:
            self._init_db_session()
        else:
            self.current_db_session_id = None

    def _load_config(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def _init_event_log(self):
        log_dir = "data/logs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(log_dir, f"session_{timestamp}.csv")
        self._log_headers_written = False

    def _init_db_session(self):
        db = SessionLocal()
        try:
            # conductor_id = 1 as default
            nueva_sesion = SesionConduccion(conductor_id=1, inicio_sesion=get_peru_time())
            db.add(nueva_sesion)
            db.commit()
            db.refresh(nueva_sesion)
            self.current_db_session_id = nueva_sesion.id
        finally:
            db.close()

    def log_event(self, data):
        """Persiste un evento de detección en CSV y BD para análisis posterior."""
        try:
            write_header = not self._log_headers_written
            with open(self.log_file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if write_header:
                    writer.writeheader()
                    self._log_headers_written = True
                writer.writerow(data)
                
            # Log to DB only if it's an important event and not in edge mode
            if not self.edge_mode and (data.get("alert_level", 0) > 0 or data.get("event_type") != "normal"):
                db = SessionLocal()
                try:
                    evento = EventoFatiga(
                        sesion_id=self.current_db_session_id,
                        tipo_evento=data.get("event_type", "desconocido"),
                        nivel_riesgo=float(data.get("risk_score", 0)),
                        ear_registrado=float(data.get("ear", 0)),
                        mar_registrado=float(data.get("mar", 0)),
                        timestamp=get_peru_time()
                    )
                    db.add(evento)
                    db.commit()
                finally:
                    db.close()
        except Exception as e:
            logger.error(f"Error al guardar log de evento: {e}")

    def process_frame(self, frame):
        metrics = self.frame_processor.process(frame)
        if metrics is None:
            return frame, None
            
        t = self.risk_engine.get_thresholds()
        
        log_data = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "ear": round(metrics["ear"], 3), "mar": round(metrics["mar"], 3),
            "perclos": round(self.last_perclos, 3), "pitch": round(metrics["pitch"], 1),
            "eye_closed_prob": round(metrics["eye_prob"], 3) if metrics["eye_prob"] is not None else 0,
            "risk_score": 0, "alert_level": 0, "event_type": "normal", "explanation": "OK"
        }

        # --- FASE 1: CALIBRACIÓN ---
        if not self.profile.get("initialized", False):
            self.calibrator.update(metrics["ear"], metrics["mar"], metrics["pitch"], valid=True)
            log_data["event_type"] = "calibrating"
            log_data["explanation"] = f"Calibrando... {int(self.calibrator.progress() * 100)}%"
            if self.calibrator.is_complete():
                calib_data = self.calibrator.build_profile_data()
                self.profile = self.profile_manager.initialize_from_calibration(self.profile, calib_data)
                self.risk_engine.set_profile(self.profile)
                self.eye_counter = 0
                self.pitch_counter = 0
                self.yaw_counter = 0
                self.perclos_calc = PerclosCalculator(window_seconds=60)
                logger.info(f"Calibración completa. Perfil: EAR={self.profile.get('ear_baseline')}, "
                           f"MAR={self.profile.get('mar_baseline')}, PITCH={self.profile.get('pitch_baseline')}")
            return frame, log_data

        # --- FASE 2: DETECCIÓN ESTABLE ---
        
        # Ojos
        if metrics["ear"] < t["ear_warning"]: self.eye_counter += 1
        else: self.eye_counter = 0
            
        # PITCH (Caída de cabeza)
        pitch_baseline = self.profile.get("pitch_baseline", 70.0)
        if (pitch_baseline - metrics["pitch"]) > t["pitch_down_delta"]:
            self.pitch_counter += 1
        else:
            self.pitch_counter = 0
            
        # YAW
        if abs(metrics["yaw"]) > t["yaw_distraction"]:
            self.yaw_counter += 1
        else:
            self.yaw_counter = 0

        # PERCLOS
        perclos, _, _, _ = self.perclos_calc.update(metrics["ear"] < t["ear_warning"])
        self.last_perclos = perclos

        # EVALUACIÓN DE RIESGO
        yawning, _ = self.yawn_detector.update(metrics["mar"])
        
        risk_score, alert_level, event_type, explanation = self.risk_engine.evaluate(
            ear=metrics["ear"], mar=metrics["mar"], perclos=perclos,
            eye_prob=metrics["eye_prob"], eye_counter=self.eye_counter,
            pitch_counter=self.pitch_counter, yaw_counter=self.yaw_counter,
            yawning=yawning
        )

        # Memoria temporal: filtrar picos falsos
        self.temporal_memory.update(
            ear=metrics["ear"], mar=metrics["mar"], perclos=perclos,
            pitch=metrics["pitch"], eye_prob=metrics["eye_prob"],
            risk_score=risk_score
        )
        analysis = self.temporal_memory.analyze()
        if analysis["fake_peak"] and alert_level >= 2:
            # Degradar alerta si es un pico falso transitorio
            risk_score = int(analysis["avg_risk"])
            alert_level = max(0, alert_level - 1)
            event_type = "fatigue" if alert_level == 1 else "normal"
            explanation = "Pico transitorio filtrado."
        
        log_data.update({
            "risk_score": risk_score, "alert_level": alert_level,
            "event_type": event_type, "explanation": explanation, "perclos": perclos
        })

        # Persistir evento
        self.log_event(log_data)

        self.orchestrator.handle_event(frame, event_type, alert_level, explanation)
        return frame, log_data

    def shutdown(self):
        self.orchestrator.shutdown()
        logger.info(f"Sesión finalizada. Log guardado en: {self.log_file_path}")
        
        # Cerrar sesión en BD
        if not self.edge_mode:
            db = SessionLocal()
            try:
                if hasattr(self, 'current_db_session_id'):
                    sesion = db.query(SesionConduccion).filter(SesionConduccion.id == self.current_db_session_id).first()
                    if sesion:
                        sesion.fin_sesion = get_peru_time()
                        db.commit()
            finally:
                db.close()
