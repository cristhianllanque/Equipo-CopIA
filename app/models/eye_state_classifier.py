import os
import cv2
import numpy as np

try:
    # Only import if tensorflow is installed
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

class EyeStateClassifier:
    def __init__(self, model_path="models_store/eye_classifier/mobilenetv2_eye_classifier.h5"):
        self.model_path = model_path
        self.model = None
        self.input_shape = (224, 224)
        
        if TF_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.model = load_model(self.model_path)
                print(f"[INFO] Loaded eye classifier from {self.model_path}")
            except Exception as e:
                print(f"[WARNING] Failed to load eye classifier: {e}")
        else:
            if not TF_AVAILABLE:
                print("[WARNING] TensorFlow not installed. Deep Learning eye classifier disabled.")
            else:
                print(f"[WARNING] Eye classifier model not found at {self.model_path}. Using EAR fallback.")

    def is_available(self):
        return self.model is not None

    def predict_eye_closed_prob(self, eye_roi, ear_value=None):
        """
        Predict probability of eye being closed.
        Returns a float between 0.0 and 1.0.
        Si el modelo no está, usa un mock basado en el valor EAR.
        """
        if not self.is_available():
            # MOCK FALLBACK
            if ear_value is not None:
                # Si EAR es menor a 0.20, alta probabilidad de cerrado
                prob = max(0.0, min(1.0, 1.0 - (ear_value / 0.30)))
                return float(prob)
            return 0.0
            
        if eye_roi is None or eye_roi.size == 0:
            return 0.0
            
        try:
            img = cv2.resize(eye_roi, self.input_shape)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                
            img = img.astype("float32") / 255.0
            img = np.expand_dims(img, axis=0)
            
            prediction = self.model.predict(img, verbose=0)
            
            if prediction.shape[-1] == 1:
                return float(prediction[0][0])
            elif prediction.shape[-1] == 2:
                return float(prediction[0][1])
            else:
                return float(prediction[0][0])
                
        except Exception as e:
            print(f"[ERROR] Eye prediction failed: {e}")
            return 0.0
