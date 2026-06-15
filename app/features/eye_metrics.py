import numpy as np

# ==============================
# DISTANCIA EUCLIDIANA
# ==============================
def euclidean_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


# ==============================
# CÁLCULO DE EAR
# ==============================
def calculate_ear(eye_points):
    # eye_points: lista de 6 puntos [(x,y), ...]

    p1, p2, p3, p4, p5, p6 = eye_points

    vertical1 = euclidean_distance(p2, p6)
    vertical2 = euclidean_distance(p3, p5)
    horizontal = euclidean_distance(p1, p4)

    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear


# ==============================
# ÍNDICES DE OJOS (MediaPipe)
# ==============================
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]


# ==============================
# EXTRAER PUNTOS DEL OJO
# ==============================
def extract_eye_points(landmarks, indices, width, height):
    points = []
    for idx in indices:
        x = int(landmarks[idx].x * width)
        y = int(landmarks[idx].y * height)
        points.append((x, y))
    return points


# índices de boca (MediaPipe)
MOUTH_IDX = [61, 81, 13, 311, 308, 402, 14, 178]


def calculate_mar(mouth_points):
    p1, p2, p3, p4, p5, p6, p7, p8 = mouth_points

    vertical = (
        euclidean_distance(p3, p7) +
        euclidean_distance(p4, p6) +
        euclidean_distance(p2, p8)
    )

    horizontal = euclidean_distance(p1, p5)

    mar = vertical / (2.0 * horizontal)
    return mar


def extract_mouth_points(landmarks, indices, width, height):
    points = []
    for idx in indices:
        x = int(landmarks[idx].x * width)
        y = int(landmarks[idx].y * height)
        points.append((x, y))
    return points