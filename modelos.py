import enum
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey, Numeric, Enum, CHAR, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

from base_de_datos import Base

class EstadoReservacion(enum.Enum):
    CREADA = "CREADA"
    PAGADA = "PAGADA"
    CANCELADA = "CANCELADA"

class DenominacionBoleto(enum.Enum):
    VIP = "VIP"
    General = "General"
    Preferente = "Preferente"

class Cliente(Base):
    __tablename__ = 'cliente'
    id_cliente = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(200), nullable=False)
    telefono = Column(String(10), nullable=False)
    reservaciones = relationship("Reservacion", back_populates="cliente")

class Evento(Base):
    __tablename__ = 'evento'
    id_evento = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(350))
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)    
    lugar = Column(String(125), nullable=False)
    capacidad = Column(Integer, nullable=False)
    tipos_boleto = relationship("TipoBoleto", back_populates="evento")

class Reservacion(Base):
    __tablename__ = 'reservacion'
    id_reservacion = Column(Integer, primary_key=True)
    estado = Column(Enum(EstadoReservacion), nullable=False, default=EstadoReservacion.CREADA)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    cancelada_en = Column(DateTime(timezone=True), nullable=True)
    cliente = relationship("Cliente", back_populates="reservaciones")
    boletos = relationship("Boleto", back_populates="reservacion")

class Asiento(Base):
    __tablename__ = 'asiento'
    id_asiento = Column(Integer, primary_key=True)
    fila = Column(CHAR(1), nullable=False)
    numero = Column(Integer, nullable=False)

class TipoBoleto(Base):
    __tablename__ = 'tipo_boleto'
    id_tipo_boleto = Column(Integer, primary_key=True)
    id_evento = Column(Integer, ForeignKey('evento.id_evento'), nullable=False)
    denominacion = Column(Enum(DenominacionBoleto), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    cupo = Column(Integer, nullable=False)  # Cupo total disponible
    evento = relationship("Evento", back_populates="tipos_boleto")

class Boleto(Base):
    __tablename__ = 'boleto'
    id_boleto = Column(Integer, primary_key=True)
    id_reservacion = Column(Integer, ForeignKey('reservacion.id_reservacion'), nullable=False)
    id_asiento = Column(Integer, ForeignKey('asiento.id_asiento'), nullable=False)
    id_evento = Column(Integer, ForeignKey('evento.id_evento'), nullable=False)
    reservacion = relationship("Reservacion", back_populates="boletos")