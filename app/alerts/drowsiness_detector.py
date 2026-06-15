class DrowsinessDetector:
    def __init__(self, ear_threshold=0.2, max_frames=20):
        self.ear_threshold = ear_threshold
        self.max_frames = max_frames
        self.counter = 0
        self.drowsy = False

    def update(self, ear):
        if ear < self.ear_threshold:
            self.counter += 1

            if self.counter >= self.max_frames:
                self.drowsy = True
        else:
            self.counter = 0
            self.drowsy = False

        return self.drowsy, self.counter