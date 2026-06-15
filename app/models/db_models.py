from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    perfil = relationship("PerfilCalibracion", back_populates="conductor", uselist=False)
    sesiones = relationship("SesionConduccion", back_populates="conductor")

class PerfilCalibracion(Base):
    __tablename__ = "perfiles_calibracion"

    id = Column(Integer, primary_key=True, index=True)
    conductor_id = Column(Integer, ForeignKey("conductores.id"), unique=True)
    
    ear_baseline = Column(Float, default=0.28)
    mar_baseline = Column(Float, default=0.30)
    pitch_baseline = Column(Float, default=0.0)
    yaw_baseline = Column(Float, default=0.0)
    normal_frames_observed = Column(Integer, default=0)
    initialized = Column(Boolean, default=False)
    last_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conductor = relationship("Conductor", back_populates="perfil")

class SesionConduccion(Base):
    __tablename__ = "sesiones_conduccion"

    id = Column(Integer, primary_key=True, index=True)
    conductor_id = Column(Integer, ForeignKey("conductores.id"))
    inicio_sesion = Column(DateTime, default=datetime.utcnow)
    fin_sesion = Column(DateTime, nullable=True)

    conductor = relationship("Conductor", back_populates="sesiones")
    eventos = relationship("EventoFatiga", back_populates="sesion")

class EventoFatiga(Base):
    __tablename__ = "eventos_fatiga"

    id = Column(Integer, primary_key=True, index=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_conduccion.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    tipo_evento = Column(String(50)) # e.g. "somnolencia_critica", "bostezo"
    nivel_riesgo = Column(Float) # 0 a 100
    ear_registrado = Column(Float)
    mar_registrado = Column(Float)

    sesion = relationship("SesionConduccion", back_populates="eventos")
