import speech_recognition as sr


class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.last_result = None

    def clear_last_result(self):
        self.last_result = None

    def listen_async(self, timeout=4, phrase_time_limit=3):
        """
        Escucha de forma asíncrona para no bloquear el hilo principal (cámara).
        """
        if getattr(self, 'is_listening', False):
            return

        self.is_listening = True
        self.listen_finished = False
        self.last_result = None

        def worker():
            res = self.listen_once(timeout, phrase_time_limit)
            self.last_result = res
            self.listen_finished = True
            self.is_listening = False

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def listen_once(self, timeout=4, phrase_time_limit=3):
        """
        Escucha UNA sola vez con parámetros configurables.
        Compatible con main.py
        """
        try:
            with sr.Microphone() as source:
                print("[LISTENER] Escuchando respuesta del conductor...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            text = self.recognizer.recognize_google(audio, language="es-ES")
            text = text.lower().strip()

            print("[LISTENER] Detectado:", text)
            self.last_result = text
            return text

        except Exception:
            return None