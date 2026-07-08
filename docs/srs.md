# Especificación de Requerimientos de Software (SRS) - IEEE 29148

## 1. Introducción
**Propósito:** Este documento define los requisitos para el sistema CopIA, una herramienta de asistencia al conductor basada en inteligencia artificial adaptativa y visión computacional para la prevención de accidentes por fatiga y somnolencia.

**Alcance:** CopIA se ejecutará en hardware local (ej. laptop o sistema embebido en cabina), procesará video en tiempo real usando una cámara estándar, y presentará alertas tanto visuales como auditivas. Incluye una interfaz gráfica web local para visualizar el historial y métricas en vivo.

## 2. Descripción General
CopIA consta de tres componentes principales:
1. **Motor de Inferencia:** Analiza la geometría facial para detectar pestañeos (EAR), bostezos (MAR) e inclinación de la cabeza (Pitch/Yaw).
2. **Motor Adaptativo:** Aprende los patrones naturales del conductor durante los primeros segundos para calibrar los umbrales de riesgo.
3. **Dashboard e Historial:** Una base de datos MySQL guarda eventos críticos para auditoría, visibles a través de una interfaz React.

## 3. Requisitos Funcionales
- **RF-01 (Calibración):** El sistema debe calibrar automáticamente el perfil del conductor (Baseline EAR/MAR/Pitch) durante los primeros 12 segundos de uso.
- **RF-02 (Detección Ocular):** El sistema debe calcular el índice EAR y alertar si los ojos están cerrados más de 1 segundo continuo.
- **RF-03 (PERCLOS):** El sistema debe calcular el porcentaje de cierre ocular en una ventana móvil de 60 segundos. Si excede el 15%, emitirá una alerta de fatiga.
- **RF-04 (Bostezos):** El sistema detectará bostezos prolongados mediante el índice MAR y lo registrará en la base de datos.
- **RF-05 (Dashboard):** El sistema expondrá una API REST local y una UI web que mostrará el nivel de riesgo del 0 al 100.
- **RF-06 (Persistencia):** Todo evento que exceda el nivel de riesgo 1 debe registrarse en la base de datos vinculada a la sesión actual.

## 4. Requisitos No Funcionales
- **RNF-01 (Desempeño):** El procesamiento de cada frame de video debe ejecutarse en menos de 50 milisegundos para garantizar un mínimo de 20 FPS.
- **RNF-02 (Precisión):** El sistema no debe emitir falsos positivos por parpadeos normales. Los picos falsos deben filtrarse temporalmente.
- **RNF-03 (Despliegue):** El sistema debe poder correr de forma offline sin depender de APIs en la nube, usando modelos locales (ej. MediaPipe y MobileNet).
- **RNF-04 (Mantenibilidad):** El código debe seguir principios SOLID y estar documentado arquitectónicamente con C4 y UML.
