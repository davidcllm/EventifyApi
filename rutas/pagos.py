from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from base_de_datos import obtener_db
from modelos import Reservacion, EstadoReservacion, Boleto, TipoBoleto


enrutador = APIRouter(prefix="/reservations", tags=["Pagos y Cancelaciones"])

# 5.1 Pagar (Validar cupos y cambiar estado a PAGADA)
@enrutador.post("/{id_reservacion}/pay")
def pagar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    reservacion = db.query(Reservacion).filter(
        Reservacion.id_reservacion == id_reservacion
    ).first()

    if not reservacion:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "NOT_FOUND", "message": "No se encontró la reservación"}
        )

    if reservacion.estado != EstadoReservacion.CREADA:
        raise HTTPException(
            status_code=409,
            detail={"error_code": "INVALID_STATE", "message": "Solo reservaciones CREADA pueden pagarse"}
        )

    # Agrupar boletos en ESTA reservación por tipo de boleto
    items = (
        db.query(
            Boleto.id_tipo_boleto.label("ticket_type_id"),
            func.count(Boleto.id_boleto).label("quantity")
        )
        .filter(Boleto.id_reservacion == id_reservacion)
        .group_by(Boleto.id_tipo_boleto)
        .all()
    )

    if not items:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "VALIDATION_ERROR", "message": "La reservación no tiene boletos"}
        )

    # Determinar el evento de esa reservación vía boletos
    event_row = db.query(Boleto.id_evento).filter(Boleto.id_reservacion == id_reservacion).first()
    event_id = event_row[0] if event_row else None

    if event_id is None:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "VALIDATION_ERROR", "message": "No se pudo determinar el evento de la reservación"}
        )

    detalles_error = []

    for item in items:
        tipo = db.query(TipoBoleto).filter(
            TipoBoleto.id_tipo_boleto == item.ticket_type_id
        ).first()

        if not tipo:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": "Tipo de boleto no existe",
                    "details": {"ticket_type_id": item.ticket_type_id}
                }
            )

        # Vendidos = boletos PAGADOS del MISMO evento y MISMO tipo
        vendidos = (
            db.query(func.count(Boleto.id_boleto))
            .join(Reservacion, Reservacion.id_reservacion == Boleto.id_reservacion)
            .filter(
                Reservacion.estado == EstadoReservacion.PAGADA,
                Boleto.id_evento == event_id,
                Boleto.id_tipo_boleto == item.ticket_type_id
            )
            .scalar()
        ) or 0

        disponibles = int(tipo.cupo) - int(vendidos)

        if int(item.quantity) > disponibles:
            detalles_error.append({
                "ticket_type_id": item.ticket_type_id,
                "requested": int(item.quantity),
                "available": max(0, int(disponibles))
            })

    if detalles_error:
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "INSUFFICIENT_QUOTA",
                "message": "Not enough tickets available for one or more categories.",
                "details": detalles_error
            }
        )
    #Pagar
    reservacion.estado = EstadoReservacion.PAGADA
    reservacion.paid_at = datetime.now(timezone.utc).replace(microsecond=0)

    db.commit()
    db.refresh(reservacion)

    # Total = suma del precio por cada boleto (una fila por boleto)
    total = (
        db.query(func.sum(TipoBoleto.precio))
        .join(Boleto, Boleto.id_tipo_boleto == TipoBoleto.id_tipo_boleto)
        .filter(Boleto.id_reservacion == id_reservacion)
        .scalar()
    ) or 0

    return {
        "id": reservacion.id_reservacion,
        "status": reservacion.estado.value,
        "paid_at": reservacion.paid_at.isoformat(),
        "totals": {"currency": "MXN", "total": float(total)}
    }

# 5.2 Cancelar reservación
@enrutador.post("/{id_reservacion}/cancel")
def cancelar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    reservacion = db.query(Reservacion).filter(
        Reservacion.id_reservacion == id_reservacion
    ).first()

    if not reservacion:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "NOT_FOUND", "message": "No se encontró la reservación"}
        )

    if reservacion.estado == EstadoReservacion.PAGADA:
        raise HTTPException(
            status_code=409,
            detail={"error_code": "INVALID_STATE", "message": "No se puede cancelar una reservación pagada"}
        )

    if reservacion.estado == EstadoReservacion.CANCELADA:
        return {
            "id": reservacion.id_reservacion,
            "status": reservacion.estado.value,
            "canceled_at": reservacion.cancelada_en.isoformat()
        }

    reservacion.estado = EstadoReservacion.CANCELADA
    reservacion.cancelada_en = datetime.now(timezone.utc).replace(microsecond=0)

    db.commit()
    db.refresh(reservacion)

    return {
        "id": reservacion.id_reservacion,
        "status": reservacion.estado.value,
        "canceled_at": reservacion.cancelada_en.isoformat()
    }
