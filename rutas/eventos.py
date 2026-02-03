from datetime import datetime, time, timedelta 
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from base_de_datos import obtener_db
from datetime import date
from pydantic import BaseModel
from modelos import Evento

'''
Se crea esta clase para que funcione como un esquema de entrada y 
que se pueda validar los datos que se envian, así como que fastapi pueda
detectar que los datos que entran están en un JSON y que se puedan convertir
a un objeto de python
'''
class EventoIn(BaseModel):
    nombre: str
    descripcion: str | None = None
    fecha_inicio: datetime
    lugar: str
    capacidad: int

enrutador = APIRouter(prefix="/events", tags=["Eventos"])

@enrutador.post("/")
def crear_evento(evento: EventoIn, db: Session = Depends(obtener_db)):
    # 2.1 Crear evento
    nuevo_evento = Evento(
        nombre=evento.nombre,
        descripcion=evento.descripcion,
        fecha_inicio=evento.fecha_inicio,
        lugar=evento.lugar,
        capacidad=evento.capacidad
    )

    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)

    return nuevo_evento

@enrutador.get("/")
def listar_eventos(desde: date, hasta: date, db: Session = Depends(obtener_db)):
    # 2.2 Listar eventos por rango de fechas
    inicio = datetime.combine(desde, time.min)  # cambia el formato de date a datetime de ese día a las 00:00:00
    fin = datetime.combine(hasta + timedelta(days=1), time.min)  # cambia el formato de date a datetime del siguiente día a las 00:00:00

    eventos = (
        db.query(Evento)
        .filter(Evento.fecha_inicio >= inicio,
                Evento.fecha_inicio < fin)
        .order_by(Evento.fecha_inicio.asc())
        .all()
    )

    return [
        {
            "id": e.id_evento,
            "nombre": e.nombre,
            "descripcion": e.descripcion,
            "fecha_inicio": e.fecha_inicio.isoformat(),
            "lugar": e.lugar,
            "capacidad": e.capacidad
        }
        for e in eventos
    ]

@enrutador.get("/{id_evento}")
def obtener_evento_con_categorias(id_evento: int, db: Session = Depends(obtener_db)):
    # 2.3 Obtener evento con sus categorías
    pass