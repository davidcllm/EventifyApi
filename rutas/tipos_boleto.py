from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from base_de_datos import obtener_db
from modelos import Evento, TipoBoleto, DenominacionBoleto

enrutador = APIRouter(prefix="/events", tags=["Tipos de Boleto"])

class DenominacionBoletoSchema(str, Enum):
    VIP = "VIP"
    GENERAL = "GENERAL"
    PREFERENTE = "PREFERENTE"

class TipoBoletoCreate(BaseModel):
    name: DenominacionBoletoSchema
    price: Decimal
    quota: int

class TipoBoletoResponse(BaseModel):
    id: int
    event_id: int
    name: DenominacionBoletoSchema
    price: Decimal
    quota: int

    class Config:
        orm_mode = True

@enrutador.post("/{id_evento}/ticket-types", response_model=TipoBoletoResponse, status_code=status.HTTP_201_CREATED)
def crear_tipo_boleto(id_evento: int, datos: TipoBoletoCreate, db: Session = Depends(obtener_db)):
    # 3.1 Crear tipo de boleto por evento

    # Primero se comprueba que el eveto exista, por lo que le pasamos el id,
    # si no, devuelve un respuesta de tipo 404 (Not Found).
    evento = db.query(Evento).filter(Evento.id_evento == event_id).first()
    if not evento:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    # En caso de cumplir con lo anterior, creamos el nuevo tipo.
    nuevo_tipo = TipoBoleto(
        id_evento=event_id,
        denominacion=DenominacionBoleto[datos.name],
        precio=datos.price,
        cupo=datos.quota
    )

    db.add(nuevo_tipo)
    db.commit()
    db.refresh(nuevo_tipo)

    # Devolvemos la respuesta limpia, que sera de tipo 201.
    return {
        "id": nuevo_tipo.id_tipo_boleto,
        "event_id": nuevo_tipo.id_evento,
        "name": nuevo_tipo.denominacion.value,
        "price": nuevo_tipo.precio,
        "quota": nuevo_tipo.cupo
    }
