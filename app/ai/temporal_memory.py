import collections
import time

class TemporalMemory:
    def __init__(self, window_seconds=10, fps_estimate=30):
        self.window_seconds = window_seconds
        self.max_frames = int(window_seconds * fps_estimate)
        
        self.ears = collections.deque(maxlen=self.max_frames)
        self.mars = collections.deque(maxlen=self.max_frames)
        self.perclos = collections.deque(maxlen=self.max_frames)
        self.pitches = collections.deque(maxlen=self.max_frames)
        self.eye_probs = collections.deque(maxlen=self.max_frames)
        self.risk_scores = collections.deque(maxlen=self.max_frames)
        
    def update(self, ear, mar, perclos, pitch, eye_prob, risk_score):
        self.ears.append(ear)
        self.mars.append(mar)
        self.perclos.append(perclos)
        self.pitches.append(pitch)
        
        if eye_prob is not None:
            self.eye_probs.append(eye_prob)
            
        self.risk_scores.append(risk_score)
        
    def get_sustained_risk(self):
        if len(self.risk_scores) == 0:
            return 0.0
        return sum(self.risk_scores) / len(self.risk_scores)
        
    def get_trend(self, data_list):
        if len(data_list) < 2:
            return 0.0
        # Simple trend: diff between last half and first half average
        half = len(data_list) // 2
        first_half = list(data_list)[:half]
        second_half = list(data_list)[half:]
        
        avg_first = sum(first_half) / len(first_half) if len(first_half) > 0 else 0
        avg_second = sum(second_half) / len(second_half) if len(second_half) > 0 else 0
        
        return avg_second - avg_first
        
    def analyze(self):
        avg_risk = self.get_sustained_risk()
        risk_trend = self.get_trend(self.risk_scores)
        
        # Filter fake peaks: if current risk is high but sustained is low and trend is not growing fast
        current_risk = self.risk_scores[-1] if self.risk_scores else 0
        fake_peak = (current_risk > 60 and avg_risk < 30 and risk_trend < 10)
        
        return {
            "avg_risk": avg_risk,
            "risk_trend": risk_trend,
            "sustained_risk": avg_risk,
            "fake_peak": fake_peak
        }
