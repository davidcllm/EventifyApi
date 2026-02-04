from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from base_de_datos import obtener_db
from datetime import datetime
from modelos import Reservacion, ItemReservacion, TipoBoleto, Evento
from esquemas import ReservationCreate, ItemCreate, ReservationResponse, EstadoReservacion, ReservationItemResponse, Totals

enrutador = APIRouter(prefix="/reservations", tags=["Reservaciones"])


@enrutador.post("/", response_model=ReservationResponse, status_code=201)
def crear_reservacion(data: ReservationCreate, db: Session = Depends(obtener_db)):
    # 4.1 Crear reservación

    nueva_reservacion = Reservacion(
        client_id=data.client_id,
        event_id=data.event_id,
        status=EstadoReservacion.CREADA,
        created_at=datetime.timezone.utcnow()
    )
    db.add(nueva_reservacion)
    db.commit()
    db.refresh(nueva_reservacion)
    return nueva_reservacion

@enrutador.put("/{id_reservacion}/items", response_model=ReservationResponse)
def actualizar_item_reservacion(id_reservacion: int, item_data: ItemCreate, db: Session = Depends(obtener_db)):
    # 4.2 Agregar o actualizar ítem en reservación (Solo si estado es CREADA)
    item_existe = db.query(ItemReservacion).filter(ItemReservacion.reservacion_id == id_reservacion,
                                                  ItemReservacion.tipo_boleto_id == item_data.ticket_type_id).first()
    if item_existe:
        item_existe.cantidad = item_data.quantity
    else:
        nuevo_item = ItemReservacion(
            reservacion_id=id_reservacion,
            tipo_boleto_id=item_data.ticket_type_id,
            cantidad=item_data.quantity
        )
        db.add(nuevo_item)
    db.commit()
    return consultar_reservacion(id_reservacion, db)

@enrutador.delete("/{id_reservacion}/items/{id_tipo_boleto}", response_model=ReservationResponse)
def eliminar_item_reservacion(id_reservacion: int, id_tipo_boleto: int, db: Session = Depends(obtener_db)):
    # 4.3 Eliminar ítem de reservación
    item = db.query(ItemReservacion).filter(ItemReservacion.reservacion_id == id_reservacion,
                                            ItemReservacion.tipo_boleto_id == id_tipo_boleto).first()
    if item:
        event_id_temporal = item.tipo_boleto.event_id
        db.delete(item)
        db.commit()
        return consultar_reservacion(id_reservacion, db)
    else:
        primer_item = db.query(ItemReservacion).filter(ItemReservacion.reservacion_id == id_reservacion).first()
        return consultar_reservacion(id_reservacion, db)

    

@enrutador.get("/{id_reservacion}", response_model=ReservationResponse)
def consultar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    # 4.4 Consultar reservación con items
    primer_item = db.query(ItemReservacion).filter(ItemReservacion.reservacion_id == id_reservacion).first()
    return consultar_reservacion(id_reservacion, db)