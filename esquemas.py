from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal
from modelos import EstadoReservacion, DenominacionBoleto

# validacion de los datos de entrada


#RESERVACIONES
# objeto "totals" 
class Totals(BaseModel):
    currency: str = "MXN"
    total: float

# item dentro de la respuesta
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