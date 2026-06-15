import pygame


class Alarm:
    def __init__(self, sound_path=None):
        self.sound_path = sound_path
        self.playing = False
        self.loaded = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if sound_path:
                pygame.mixer.music.load(sound_path)
                self.loaded = True
        except Exception as e:
            print(f"[WARNING] No se pudo cargar la alarma: {e}")

    def trigger(self):
        if self.loaded and not self.playing:
            pygame.mixer.music.play(-1)
            self.playing = True

    def stop(self):
        if self.playing:
            pygame.mixer.music.stop()
            self.playing = False