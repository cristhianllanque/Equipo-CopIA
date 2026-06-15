class ResponseHandler:
    def __init__(self):
        self.positive_keywords = [
            "estoy bien",
            "estoy despierto",
            "todo bien",
            "sí",
            "si",
            "bien",
            "ok"
        ]

        self.negative_or_invalid = [
            "te encuentras bien",
            "somnolencia crítica",
            "mantén la calma",
            "mantén los ojos abiertos",
            "peligro",
            "advertencia",
            "bostezo"
        ]

    def is_driver_ok(self, text):
        if not text:
            return False

        text = text.lower().strip()

        for bad in self.negative_or_invalid:
            if bad in text:
                return False

        for good in self.positive_keywords:
            if good in text:
                return True

        return False