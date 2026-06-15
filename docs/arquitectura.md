# CopIA: Arquitectura del Sistema

El sistema CopIA está diseñado bajo un enfoque modular, integrando visión computacional, análisis temporal de inteligencia artificial y una interfaz de usuario interactiva (Dashboard).

## 1. Diagrama de Contexto (C4 Nivel 1)

```mermaid
graph TD
    User([Conductor]) -->|Video & Voz| CopIA(Sistema CopIA)
    CopIA -->|Alertas sonoras y visuales| User
    CopIA -->|Métricas e Historial| Dashboard[Dashboard de Monitoreo]
```

## 2. Diagrama de Contenedores (C4 Nivel 2)

```mermaid
graph TD
    subgraph CopIA Desktop App
        UI[Frontend: React Dashboard]
        API[Backend API: FastAPI]
        Vision[Módulo de Visión Computacional]
        AI[Motor de Riesgo y Perfilamiento]
        DB[(Base de Datos MySQL)]
    end
    
    UI -->|HTTP GET /api/status| API
    API -->|Consulta| DB
    Vision -->|Extrae EAR, MAR, PITCH| AI
    AI -->|Guarda perfil y eventos| DB
```

## 3. Diagrama de Componentes: Procesamiento de Video

```mermaid
sequenceDiagram
    participant Camera
    participant CopIASystem
    participant FrameProcessor
    participant RiskEngine
    participant Database

    Camera->>CopIASystem: Envía frame (imagen)
    CopIASystem->>FrameProcessor: process(frame)
    FrameProcessor->>CopIASystem: Devuelve métricas (EAR, MAR, Pitch)
    CopIASystem->>RiskEngine: evaluate(metrics)
    RiskEngine->>CopIASystem: Devuelve Nivel de Alerta y Score
    CopIASystem->>Database: log_event(evento_fatiga)
```

## 4. Estructura de Base de Datos

- **Conductor:** Información básica del usuario.
- **PerfilCalibracion:** Baselines (EAR, MAR) adaptados al conductor específico.
- **SesionConduccion:** Registro de inicio y fin de uso del sistema.
- **EventoFatiga:** Histórico inmutable de alertas generadas.
