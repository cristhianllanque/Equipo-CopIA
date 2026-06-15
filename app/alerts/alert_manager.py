class AlertManager:
    def __init__(self):
        pass

    def evaluate(self, ear, mar, counter, looking_down):
        # si está agachado, menos agresivo
        if looking_down:
            if counter >= 40:
                return 2
            if ear < 0.19:
                return 1
            return 0

        # crítico
        if counter >= 28:
            return 3

        # advertencia
        if counter >= 14:
            return 2

        # fatiga leve: más estricta
        if ear < 0.19 and counter >= 6:
            return 1

        return 0