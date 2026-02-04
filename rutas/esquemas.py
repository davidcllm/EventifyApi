
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal
from modelos import EstadoReservacion, DenominacionBoleto

# validacion de los datos de entrada

#CLIENTES
class ClienteBase(BaseModel):
    nombre: str
    correo: str
    telefono: str

class ClienteCreate(ClienteBase):
    pass # (POST)

class ClienteResponse(ClienteBase):
    id_cliente: int
    
    class Config:
        from_attributes = True

#EVENTOS
class EventoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: date 
    hora_inicio: time  
    lugar: str
    capacidad: int

class EventoCreate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id_evento: int

    class Config:
        from_attributes = True

# TIPOS DE BOLETO
class TipoBoletoBase(BaseModel):
    denominacion: DenominacionBoleto
    precio: float 
    cupo: int

class TipoBoletoCreate(TipoBoletoBase):
    pass # id_evento viene en la URL

class TipoBoletoResponse(TipoBoletoBase):
    id_tipo_boleto: int
    id_evento: int

    class Config:
        from_attributes = True

#RESERVACIONES
# objeto "totals" 
class Totals(BaseModel):
    currency: str = "MXN"
    total: float

# mostramos un item dentro de la respuesta
class ReservationItemResponse(BaseModel):
    ticket_type_id: int
    ticket_type_name: str
    unit_price: float
    quantity: int
    line_total: float

    class Config:
        from_attributes = True

# crea una reservación
class ReservationCreate(BaseModel):
    client_id: int
    event_id: int

# crea items
class ItemCreate(BaseModel):
    ticket_type_id: int
    quantity: int

# respuesta completa
class ReservationResponse(BaseModel):
    id: int
    client_id: int
    event_id: int 
    status: EstadoReservacion
    created_at: datetime
    items: List[ReservationItemResponse] = []
    totals: Totals 

    class Config:
        from_attributes = True
    
