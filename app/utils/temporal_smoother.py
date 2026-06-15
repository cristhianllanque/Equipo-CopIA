from collections import deque
import numpy as np


class TemporalSmoother:
    def __init__(self, window_size=10):
        self.ear_buffer = deque(maxlen=window_size)
        self.mar_buffer = deque(maxlen=window_size)

    def update(self, ear, mar):
        self.ear_buffer.append(ear)
        self.mar_buffer.append(mar)

        avg_ear = np.mean(self.ear_buffer)
        avg_mar = np.mean(self.mar_buffer)

        return avg_ear, avg_mar