from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from base_de_datos import obtener_db

enrutador = APIRouter(prefix="/events", tags=["Tipos de Boleto"])

@enrutador.post("/{id_evento}/ticket-types")
def crear_tipo_boleto(id_evento: int, db: Session = Depends(obtener_db)):
    # 3.1 Crear tipo de boleto por evento
    pass