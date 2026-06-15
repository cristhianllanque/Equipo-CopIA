import pygame
from gtts import gTTS
import threading
import time
import os
import uuid
import glob
from queue import Queue

class VoiceAssistant:
    def __init__(self, rate=175, volume=1.0, cooldown_seconds=3):
        self.cooldown = cooldown_seconds
        self.last_time = {}

        self.queue = Queue()
        self.speaking = False
        self.current_event = None

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self._cleanup_old_files()

        # hilo único de reproducción
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()

    def _cleanup_old_files(self):
        for pattern in ["temp_voice_*.mp3", "temp_voice.mp3"]:
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                except Exception:
                    pass

    def is_speaking(self):
        return self.speaking

    def _worker_loop(self):
        while True:
            message, key = self.queue.get()

            self.speaking = True
            self.current_event = key

            audio_file = f"temp_voice_{uuid.uuid4().hex}.mp3"

            try:
                tts = gTTS(text=message, lang="es")
                tts.save(audio_file)

                sound = pygame.mixer.Sound(audio_file)
                channel = sound.play()
                
                # Wait for the audio to finish playing
                while channel.get_busy():
                    pygame.time.Clock().tick(10)

            except Exception as e:
                print("Error voz:", e)

            finally:
                self.speaking = False
                self.current_event = None

                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                except:
                    pass

            self.queue.task_done()

    def speak(self, message, key=None, force=False):
        now = time.time()
        k = key or message

        # cooldown
        if not force:
            last = self.last_time.get(k, 0)
            if now - last < self.cooldown:
                return False

        # 🔥 CLAVE: si ya hay algo hablando, NO meter más cosas
        if self.speaking and not force:
            return False

        self.last_time[k] = now

        # 🔥 limpiar cola si es mensaje importante
        if force:
            with self.queue.mutex:
                self.queue.queue.clear()

        self.queue.put((message, k))
        return True

    def shutdown(self):
        pass