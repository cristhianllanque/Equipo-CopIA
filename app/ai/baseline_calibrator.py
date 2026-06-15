import time
from statistics import mean


class BaselineCalibrator:
    def __init__(self, duration_seconds=30, min_samples=45):
        self.duration_seconds = duration_seconds
        self.min_samples = min_samples
        self.started_at = time.time()

        self.ears = []
        self.mars = []
        self.pitches = []

        self.completed = False

    def progress(self):
        elapsed = time.time() - self.started_at
        return min(1.0, elapsed / self.duration_seconds)

    def is_time_complete(self):
        return (time.time() - self.started_at) >= self.duration_seconds

    def update(self, ear, mar, pitch, valid=True):
        if self.completed:
            return

        if valid:
            # filtros plausibles
            if 0.10 < ear < 0.45:
                self.ears.append(float(ear))
            if 0.10 < mar < 1.20:
                self.mars.append(float(mar))
            if -45 < pitch < 45:
                self.pitches.append(float(pitch))

        if self.is_time_complete() and len(self.ears) >= self.min_samples:
            self.completed = True

    def is_complete(self):
        return self.completed

    def build_profile_data(self):
        if len(self.ears) == 0:
            ear_baseline = 0.24
        else:
            ear_baseline = mean(self.ears)

        if len(self.mars) == 0:
            mar_baseline = 0.32
        else:
            mar_baseline = mean(self.mars)

        if len(self.pitches) == 0:
            pitch_baseline = 0.0
        else:
            pitch_baseline = mean(self.pitches)

        return {
            "ear_baseline": round(ear_baseline, 4),
            "mar_baseline": round(mar_baseline, 4),
            "pitch_baseline": round(pitch_baseline, 4),
            "normal_frames_observed": len(self.ears)
        }