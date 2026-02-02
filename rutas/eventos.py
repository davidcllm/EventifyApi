from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from base_de_datos import obtener_db
from datetime import date

enrutador = APIRouter(prefix="/events", tags=["Eventos"])

@enrutador.post("/")
def crear_evento(db: Session = Depends(obtener_db)):
    # 2.1 Crear evento
    pass

@enrutador.get("/")
def listar_eventos(desde: date, hasta: date, db: Session = Depends(obtener_db)):
    # 2.2 Listar eventos por rango de fechas
    pass

@enrutador.get("/{id_evento}")
def obtener_evento_con_categorias(id_evento: int, db: Session = Depends(obtener_db)):
    # 2.3 Obtener evento con sus categorías
    pass