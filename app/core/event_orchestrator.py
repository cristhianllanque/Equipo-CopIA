import time
from app.copiloto.voice_assistant import VoiceAssistant
from app.alerts.alarm import Alarm
from app.copiloto.listener import VoiceListener
from app.copiloto.response_handler import ResponseHandler
import cv2

class EventOrchestrator:
    def __init__(self, config=None):
        self.config = config or {}
        self.voice = VoiceAssistant(rate=175, volume=1.0, cooldown_seconds=4)
        self.alarm = Alarm("assets/alarm.wav")
        self.listener = VoiceListener()
        self.handler = ResponseHandler()
        
        self.last_voice_event = "normal"
        self.critical_active = False
        self.waiting_driver_response = False
        self.last_critical_prompt_time = 0.0
        self.driver_confirmed_until = 0.0
        
    def handle_event(self, frame, event_type, alert_level, explanation):
        current_time = time.time()
        
        if current_time < self.driver_confirmed_until and alert_level == 3:
            alert_level = 2
            event_type = "eyes_warning"
            
        if event_type == "critical":
            self._handle_critical(frame, current_time, explanation)
        elif event_type == "distraction":
            self._handle_distraction(frame, explanation)
        elif event_type == "eyes_warning":
            self._handle_eyes_warning(frame, explanation)
        elif event_type == "yawn" or event_type == "fatigue":
            self._handle_fatigue(frame, explanation)
        else:
            self._handle_normal()
            
        return event_type, alert_level
            
    def _handle_critical(self, frame, current_time, explanation):
        cv2.putText(frame, "!!! PELIGRO CRITICO !!!", (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        self.alarm.trigger()
        
        if not self.critical_active:
            self.critical_active = True
            
        if (current_time - self.last_critical_prompt_time) >= 5.0 and not self.voice.is_speaking():
            msg = "¡PELIGRO! Te estás durmiendo. ¡DESPIERTA!" if "agachado" in explanation.lower() else "¡EMERGENCIA! Somnolencia crítica detectada."
            self.voice.speak(msg, key="critical_prompt", force=True)
            self.last_critical_prompt_time = current_time
            self.waiting_driver_response = True
            
        # Lógica de respuesta por voz omitida para brevedad en este bloque
        self.last_voice_event = "critical"

    def _handle_distraction(self, frame, explanation):
        cv2.putText(frame, "DISTRACCION DETECTADA", (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)
        self.alarm.stop()
        if self.last_voice_event != "distraction":
            self.voice.speak("Mantén la vista en el camino, no te distraigas.", key="distraction")
            self.last_voice_event = "distraction"

    def _handle_eyes_warning(self, frame, explanation):
        label = "ADVERTENCIA SEMI-CRITICA" if "semi-crítica" in explanation.lower() else "AVISO: POSIBLE SUEÑO"
        cv2.putText(frame, label, (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 100, 255), 2)
        self.alarm.stop()
        
        if self.last_voice_event != explanation:
            if "semi-crítica" in explanation.lower():
                self.voice.speak("¡Cuidado! Llevas demasiado tiempo con los ojos cerrados. ¡Reacciona!", key="semi_critical")
            else:
                self.voice.speak("Ojos cerrados detectados. Mantente alerta.", key="eyes_warning")
            self.last_voice_event = explanation

    def _handle_fatigue(self, frame, explanation):
        cv2.putText(frame, "FATIGA LEVE", (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        if self.last_voice_event != "fatigue_yawn":
            self.voice.speak("Se detecta fatiga leve. Considera descansar pronto.", key="fatigue")
            self.last_voice_event = "fatigue_yawn"
            
    def _handle_normal(self):
        self.alarm.stop()
        self.critical_active = False
        self.last_voice_event = "normal"
        
    def shutdown(self):
        self.voice.shutdown()
        self.alarm.stop()
