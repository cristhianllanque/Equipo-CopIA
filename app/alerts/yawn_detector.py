class YawnDetector:
    def __init__(self, mar_threshold=0.85, min_frames=20):
        self.mar_threshold = mar_threshold
        self.min_frames = min_frames
        self.counter = 0
        self.last_mars = []
        self.window_size = 10

    def update(self, mar):
        # Filtro de bostezo real vs hablar
        # El bostezo es una apertura grande y sostenida.
        # Hablar tiene picos altos pero vuelve a bajar rápido.
        
        if mar >= self.mar_threshold:
            self.counter += 1
        else:
            # Si baja un poco pero sigue siendo relativamente alto, no resetear a cero inmediatamente
            # (evita micro-reseteos al hablar)
            if self.counter > 0 and mar > 0.5:
                pass 
            else:
                self.counter = 0

        # Un bostezo real debe durar al menos 0.6 - 1.0 segundos (dependiendo de FPS)
        is_yawning = self.counter >= self.min_frames
        return is_yawning, self.counter