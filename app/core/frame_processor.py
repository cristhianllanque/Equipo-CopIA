import cv2
import numpy as np
from app.vision.face_mesh import FaceMeshDetector
from app.features.eye_metrics import (
    calculate_ear, extract_eye_points, LEFT_EYE_IDX, RIGHT_EYE_IDX,
    calculate_mar, extract_mouth_points, MOUTH_IDX
)
from app.features.head_pose import HeadPoseEstimator
from app.utils.temporal_smoother import TemporalSmoother

class FrameProcessor:
    def __init__(self, eye_classifier=None):
        self.detector = FaceMeshDetector()
        self.head_pose = HeadPoseEstimator()
        self.smoother = TemporalSmoother(window_size=10)
        self.eye_classifier = eye_classifier

    def process(self, frame):
        h, w, _ = frame.shape
        results = self.detector.process(frame)
        
        if not results.multi_face_landmarks:
            return None
            
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Eyes
        left_eye = extract_eye_points(landmarks, LEFT_EYE_IDX, w, h)
        right_eye = extract_eye_points(landmarks, RIGHT_EYE_IDX, w, h)
        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        ear_raw = (left_ear + right_ear) / 2.0
        
        # Eye Prediction (ambos ojos)
        eye_prob = None
        if self.eye_classifier:
            probs = []
            for eye_pts in [left_eye, right_eye]:
                x_coords = [p[0] for p in eye_pts]
                y_coords = [p[1] for p in eye_pts]
                min_x, max_x = max(0, min(x_coords)-10), min(w, max(x_coords)+10)
                min_y, max_y = max(0, min(y_coords)-10), min(h, max(y_coords)+10)
                if max_x > min_x and max_y > min_y:
                    eye_roi = frame[min_y:max_y, min_x:max_x]
                    prob = self.eye_classifier.predict_eye_closed_prob(eye_roi, ear_value=ear_raw)
                    if prob is not None:
                        probs.append(prob)
            if probs:
                eye_prob = sum(probs) / len(probs)
                
        # Mouth
        mouth = extract_mouth_points(landmarks, MOUTH_IDX, w, h)
        mar_raw = calculate_mar(mouth)
        
        ear, mar = self.smoother.update(ear_raw, mar_raw)
        
        # Head Pose
        pose = self.head_pose.estimate(landmarks, frame.shape)
        pitch = yaw = roll = 0.0
        if pose:
            pitch, yaw, roll = pose
            
        return {
            "ear_raw": ear_raw,
            "ear": ear,
            "mar": mar,
            "pitch": pitch,
            "yaw": yaw,
            "roll": roll,
            "eye_prob": eye_prob,
            "left_eye_pts": left_eye,
            "right_eye_pts": right_eye,
            "mouth_pts": mouth
        }
