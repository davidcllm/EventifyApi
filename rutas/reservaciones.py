from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from base_de_datos import obtener_db
from modelos import Reservacion, ItemReservacion, TipoBoleto, Cliente, Evento, EstadoReservacion
from esquemas import ReservationCreate, ItemCreate, ReservationResponse

enrutador = APIRouter(prefix="/reservations", tags=["Reservaciones"])


def armar_respuesta(res: Reservacion, db: Session):
    items_respuesta = []
    total_gral = 0.0

    
    for item in res.items:
        tb = item.tipo_boleto # Relación a TipoBoleto
        
        # Calculamos totales
        precio = float(tb.precio)
        cantidad = item.cantidad
        line_total = precio * cantidad
        total_gral += line_total

        items_respuesta.append({
            "ticket_type_id": tb.id_tipo_boleto,
            "ticket_type_name": tb.denominacion.value if hasattr(tb.denominacion, 'value') else str(tb.denominacion),
            "unit_price": precio,
            "quantity": cantidad,
            "line_total": line_total
        })

    return {
        "id": res.id_reservacion,         # id_reservacion = id
        "client_id": res.id_cliente,      # id_cliente = client_id
        "event_id": res.id_evento,        # id_evento = event_id
        "status": res.estado,
        "created_at": res.created_at,
        "items": items_respuesta,
        "totals": {
            "currency": "MXN",
            "total": total_gral
        }
    }

# 4.1 Crear reservación
@enrutador.post("/", response_model=ReservationResponse, status_code=201)
def crear_reservacion(data: ReservationCreate, db: Session = Depends(obtener_db)):
    # Validar existencia (Opcional pero recomendado)
    if not db.query(Cliente).filter(Cliente.id_cliente == data.client_id).first():
        raise HTTPException(404, detail={"error_code": "NOT_FOUND", "message": "Client not found"})
    if not db.query(Evento).filter(Evento.id_evento == data.event_id).first():
        raise HTTPException(404, detail={"error_code": "NOT_FOUND", "message": "Event not found"})

    nueva_reservacion = Reservacion(
        id_cliente=data.client_id, 
        id_evento=data.event_id,
        estado=EstadoReservacion.CREADA,
        created_at=datetime.utcnow()
    )
    db.add(nueva_reservacion)
    db.commit()
    db.refresh(nueva_reservacion)
    
    return armar_respuesta(nueva_reservacion, db)

# 4.2 Agregar o actualizar ítem
@enrutador.put("/{id_reservacion}/items", response_model=ReservationResponse)
def actualizar_item_reservacion(id_reservacion: int, item_data: ItemCreate, db: Session = Depends(obtener_db)):
    res = db.query(Reservacion).filter(Reservacion.id_reservacion == id_reservacion).first()
    if not res:
        raise HTTPException(404, detail={"error_code": "NOT_FOUND", "message": "Reservation not found"})

    # solo CREADA
    if res.estado != EstadoReservacion.CREADA:
        raise HTTPException(400, detail={"error_code": "INVALID_STATUS", "message": "Reservation cannot be modified"})

    # Cantidad > 0
    if item_data.quantity <= 0:
        raise HTTPException(400, detail={"error_code": "VALIDATION_ERROR", "message": "Quantity must be > 0"})

    # Mismo evento
    tipo_boleto = db.query(TipoBoleto).filter(TipoBoleto.id_tipo_boleto == item_data.ticket_type_id).first()
    if not tipo_boleto:
        raise HTTPException(404, detail={"error_code": "NOT_FOUND", "message": "Ticket Type not found"})
    
    if tipo_boleto.id_evento != res.id_evento:
        raise HTTPException(400, detail={"error_code": "INVALID_EVENT", "message": "Ticket type does not belong to event"})

    # nuestro upsert
    item_existente = db.query(ItemReservacion).filter(
        ItemReservacion.id_reservacion == id_reservacion,
        ItemReservacion.id_tipo_boleto == item_data.ticket_type_id
    ).first()

    if item_existente:
        item_existente.cantidad = item_data.quantity
    else:
        nuevo_item = ItemReservacion(
            id_reservacion=id_reservacion,
            id_tipo_boleto=item_data.ticket_type_id,
            cantidad=item_data.quantity
        )
        db.add(nuevo_item)

    db.commit()
    return armar_respuesta(res, db)

# 4.3 Eliminar ítem
@enrutador.delete("/{id_reservacion}/items/{id_tipo_boleto}", response_model=ReservationResponse)
def eliminar_item_reservacion(id_reservacion: int, id_tipo_boleto: int, db: Session = Depends(obtener_db)):
    res = db.query(Reservacion).filter(Reservacion.id_reservacion == id_reservacion).first()
    if not res:
        raise HTTPException(404, detail={"error_code": "NOT_FOUND", "message": "Reservation not found"})

    if res.estado != EstadoReservacion.CREADA:
        raise HTTPException(400, detail={"error_code": "INVALID_STATUS", "message": "Reservation cannot be modified"})

    item = db.query(ItemReservacion).filter(
        ItemReservacion.id_reservacion == id_reservacion,
        ItemReservacion.id_tipo_boleto == id_tipo_boleto
    ).first()

    if item:
        db.delete(item)
        db.commit()
    
    return armar_respuesta(res, db)

# 4.4 Consultar reservación
@enrutador.get("/{id_reservacion}", response_model=ReservationResponse)
def consultar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    res = db.query(Reservacion).filter(Reservacion.id_reservacion == id_reservacion).first()
    if not res:
        raise HTTPException(404, detail={"error_code": "NOT_FOUND", "message": "Reservation not found"})
    
    return armar_respuesta(res, db)