import enum
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey, Numeric, Enum, CHAR, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

from sqlalchemy import DateTime
from datetime import datetime, timezone

from base_de_datos import Base

class EstadoReservacion(enum.Enum):
    CREADA = "CREADA"
    PAGADA = "PAGADA"
    CANCELADA = "CANCELADA"

class DenominacionBoleto(enum.Enum):
    VIP = "VIP"
    General = "GENERAL"
    Preferente = "PREFERENTE"

class Cliente(Base):
    __tablename__ = 'cliente'
    id_cliente = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(200), nullable=False, unique=True, index=True)
    telefono = Column(String(30), nullable=False) #diferentes formatos

    #1.1 Cliente: created_at + correo único
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

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

    #1.2 Reservacion: paid_at
    paid_at = Column(DateTime(timezone=True), nullable=True) 

    boletos = relationship("Boleto", back_populates="reservacion")

class Asiento(Base):
    __tablename__ = 'asiento'
    id_asiento = Column(Integer, primary_key=True)
    fila = Column(CHAR(1), nullable=False)
    numero = Column(Integer, nullable=False)

class TipoBoleto(Base):
    __tablename__ = 'tipo_boleto'

    # Se agrega el Unique Constraint para que el nombre sea único
    __table_args__ = (
        UniqueConstraint(
            'id_evento',
            'denominacion',
            name='uq_evento_denominacion_boleto'
        ),
    )
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

    #1.3 Boleto: link a TipoBoleto
    id_tipo_boleto = Column(Integer, ForeignKey('tipo_boleto.id_tipo_boleto'), nullable=False)
    tipo_boleto = relationship("TipoBoleto")

    reservacion = relationship("Reservacion", back_populates="boletos")