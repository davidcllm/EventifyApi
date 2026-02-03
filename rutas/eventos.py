from datetime import datetime, time, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from base_de_datos import obtener_db
from datetime import date
from pydantic import BaseModel

from modelos import Evento, TipoBoleto
from base_de_datos import obtener_db

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

    if evento.capacidad <= 0:
        raise HTTPException(status_code=422, detail="La capacidad debe ser mayor a 0")
    
    if evento.fecha_inicio < datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="La fecha de inicio debe ser mayor a la fecha actual")

    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)

    return nuevo_evento

@enrutador.get("/")
def listar_eventos(desde: date, hasta: date, db: Session = Depends(obtener_db)):
    # 2.2 Listar eventos por rango de fechas
    inicio = datetime.combine(desde, time.min)  # cambia el formato de date a datetime de ese día a las 00:00:00
    fin = datetime.combine(hasta + timedelta(days=1), time.min)  # cambia el formato de date a datetime del siguiente día a las 00:00:00

    if hasta < desde:
        raise HTTPException(status_code=422, detail="'hasta' no puede ser menor que 'desde'")

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
    evento = (
        db.query(Evento)
        .options(selectinload(Evento.tipos_boleto))
        .filter(Evento.id_evento == id_evento)
        .first()
    )

    if not evento:
        raise HTTPException(status_code=404, detail="No se encontró el evento")

    tipo_boletos = []
    for t in (evento.tipos_boleto or []):
        # Esto es para manejar el enum que puede haber en este campo
        denom = getattr(t.denominacion, "value", str(t.denominacion)) # En caso de que sea un enum, usa su .value

        tipo_boletos.append({
            "id": t.id_tipo_boleto,
            "nombre": str(denom).upper(), 
            "precio": float(t.precio),     
            "cupo": t.cupo                 
        })

    return {
        "id": evento.id_evento,
        "nombre": evento.nombre,
        "descripcion": evento.descripcion,
        "fecha_inicio": evento.fecha_inicio.isoformat(),
        "lugar": evento.lugar,
        "capacidad": evento.capacidad,
        "tipo_boletos": tipo_boletos
    }
