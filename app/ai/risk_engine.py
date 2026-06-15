class ContinuousRiskEngine:
    def __init__(self, profile, config=None):
        self.profile = profile
        self.config = config or {}
        
        # Usar umbrales del config YAML o valores default
        self.fatigue_threshold = self.config.get("risk_threshold_fatigue", 40)
        self.warning_threshold = self.config.get("risk_threshold_warning", 65)
        self.critical_threshold = self.config.get("risk_threshold_critical", 88)

    def set_profile(self, profile):
        self.profile = profile

    def get_thresholds(self):
        # Usar EAR baseline del perfil calibrado para umbrales adaptativos
        ear_baseline = self.profile.get("ear_baseline", 0.24)
        ear_warning = max(0.12, ear_baseline * 0.70)  # 70% del baseline
        ear_critical = max(0.08, ear_baseline * 0.50)  # 50% del baseline

        thresholds = {
            "ear_warning": round(ear_warning, 3),
            "ear_critical": round(ear_critical, 3),
            "mar_yawn": 0.80,
            "pitch_down_delta": 100.0,
            "yaw_distraction": 42.0
        }
        return thresholds

    def evaluate(self, ear, mar, perclos, eye_prob, eye_counter, pitch_counter, yaw_counter, yawning):
        t = self.get_thresholds()
        risk_score = 0
        
        # 1. AGACHARSE (CRÍTICO)
        if pitch_counter > 50:
            return 100, 3, "critical", "Somnolencia: Cabeza caída."
        elif pitch_counter > 20:
            risk_score += 40

        # 2. OJOS
        if eye_counter > 120: 
            return 100, 3, "critical", "Microsueño detectado."
        elif eye_counter > 45:
            risk_score += 65
        elif eye_counter > 15:
            risk_score += 25

        # 3. DISTRACCIÓN
        if yaw_counter > 60:
            return 70, 2, "distraction", "¡Vista al frente!"

        if yawning:
            return 40, 1, "yawn", "Bostezo detectado."

        if perclos > 0.55:
            risk_score += 25

        # 4. Eye classifier contribuye al riesgo si está disponible
        if eye_prob is not None and eye_prob > 0.7:
            risk_score += 15

        risk_score = min(100, risk_score)
        
        if risk_score >= self.critical_threshold:
            return risk_score, 3, "critical", "Peligro de somnolencia."
        elif risk_score >= self.warning_threshold:
            return risk_score, 2, "eyes_warning", "Signos de sueño."
        elif risk_score >= self.fatigue_threshold:
            return risk_score, 1, "fatigue", "Fatiga leve."

        return risk_score, 0, "normal", "OK"