import collections

class PerclosCalculator:
    def __init__(self, window_seconds=60, fps_estimate=30):
        self.window_seconds = window_seconds
        self.fps_estimate = fps_estimate
        self.max_frames = int(window_seconds * fps_estimate)
        self.history = collections.deque(maxlen=self.max_frames)
        
    def update(self, is_closed):
        self.history.append(1 if is_closed else 0)
        
        if len(self.history) == 0:
            return 0.0, 0, 0, "normal"
            
        closed_frames = sum(self.history)
        total_frames = len(self.history)
        perclos = closed_frames / total_frames
        
        if perclos < 0.20:
            risk_level = "normal"
        elif perclos < 0.35:
            risk_level = "fatigue"
        elif perclos < 0.50:
            risk_level = "warning"
        else:
            risk_level = "critical"
            
        return perclos, total_frames, closed_frames, risk_level
