# Entrenamiento de MobileNetV2 para Clasificación de Ojos

Para mejorar la robustez de CopIA, puedes entrenar un clasificador binario (Ojo Abierto / Ojo Cerrado).

## 1. Dataset Sugerido
- **MRL Eye Dataset**: Contiene miles de imágenes de ojos en diferentes condiciones de iluminación y con/sin anteojos.
- **CEW (Closed Eyes in the Wild)**: Excelente para variabilidad real.

## 2. Preparación de Datos
1. Estructura tus carpetas:
   - `dataset/train/open/`
   - `dataset/train/closed/`
   - `dataset/val/open/`
   - `dataset/val/closed/`
2. Redimensiona las imágenes a **224x224**.
3. Normaliza los píxeles al rango [0, 1].

## 3. Arquitectura del Modelo (Keras/TensorFlow)
```python
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False # Congelar base

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2),
    layers.Dense(1, activation='sigmoid') # Salida binaria: probabilidad de ojo cerrado
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
```

## 4. Entrenamiento
- Usa `ImageDataGenerator` para aumentar los datos (rotación, brillo, zoom).
- Entrena por ~10-20 épocas.
- Descongela las últimas capas de MobileNetV2 y re-entrena con un learning rate muy bajo para hacer fine-tuning.

## 5. Exportación
Guarda el modelo como:
`models_store/eye_classifier/mobilenetv2_eye_classifier.h5`

CopIA detectará automáticamente este archivo al iniciar.
