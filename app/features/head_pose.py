import cv2
import numpy as np


class HeadPoseEstimator:
    def __init__(self):
        # puntos clave (MediaPipe)
        self.landmark_ids = [1, 33, 263, 61, 291, 199]

        # modelo 3D simple de cara
        self.model_points = np.array([
            (0.0, 0.0, 0.0),         # nariz
            (-30.0, -125.0, -30.0),  # ojo izquierdo
            (30.0, -125.0, -30.0),   # ojo derecho
            (-60.0, 70.0, -60.0),    # boca izquierda
            (60.0, 70.0, -60.0),     # boca derecha
            (0.0, 150.0, -100.0)     # mentón
        ])

    def estimate(self, landmarks, frame_shape):
        h, w = frame_shape[0], frame_shape[1]

        image_points = []

        for idx in self.landmark_ids:
            lm = landmarks[idx]
            x = int(float(lm.x) * w)
            y = int(float(lm.y) * h)
            image_points.append((x, y))

        image_points = np.array(image_points, dtype="double")

        # cámara
        focal_length = w
        center = (w / 2, h / 2)

        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        dist_coeffs = np.zeros((4, 1))

        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return None

        # convertir a ángulos
        rmat, _ = cv2.Rodrigues(rotation_vector)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        pitch = angles[0]  # arriba/abajo
        yaw = angles[1]    # izquierda/derecha
        roll = angles[2]   # inclinación

        return pitch, yaw, roll