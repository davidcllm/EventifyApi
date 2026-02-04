from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from base_de_datos import obtener_db
from modelos import Reservacion, EstadoReservacion, Boleto, TipoBoleto


enrutador = APIRouter(prefix="/reservations", tags=["Pagos y Cancelaciones"])

# 5.1 Pagar (Validar cupos y cambiar estado a PAGADA)
# POST /reservations/{id_reservacion}/pay

# Solo permite pagar si la reservación está en CREADA
# Valida cupos por tipo de boleto contra boletos ya PAGADOS
# Si hay cupo: cambia a PAGADA y registra paid_at
# Si no hay cupo: devuelve 409 con details (requested/available)
@enrutador.post("/{id_reservacion}/pay")
def pagar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
     # Buscar la reservación por id
    reservacion = db.query(Reservacion).filter(
        Reservacion.id_reservacion == id_reservacion
    ).first()

     # Si no existe, 404 con error JSON consistente
    if not reservacion:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "NOT_FOUND", "message": "No se encontró la reservación"}
        )

    # Solo reservaciones CREADA se pueden pagar
    if reservacion.estado != EstadoReservacion.CREADA:
        raise HTTPException(
            status_code=409,
            detail={"error_code": "INVALID_STATE", "message": "Solo reservaciones CREADA pueden pagarse"}
        )

    # Agrupar boletos en ESTA reservación por tipo de boleto
    # ticket_type_id: id del tipo de boleto
    # quantity: cuántos boletos de ese tipo tiene la reservación
    items = (
        db.query(
            Boleto.id_tipo_boleto.label("ticket_type_id"),
            func.count(Boleto.id_boleto).label("quantity")
        )
        .filter(Boleto.id_reservacion == id_reservacion)
        .group_by(Boleto.id_tipo_boleto)
        .all()
    )

    # Si no tiene boletos, no se puede pagar
    if not items:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "VALIDATION_ERROR", "message": "La reservación no tiene boletos"}
        )

    # Determinar el evento de esa reservación vía boletos
    # Esto evita depender de que Reservacion tenga id_evento
    event_row = db.query(Boleto.id_evento).filter(Boleto.id_reservacion == id_reservacion).first()
    event_id = event_row[0] if event_row else None

    # Si no se puede determinar el evento, se devuelve error de validación
    if event_id is None:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "VALIDATION_ERROR", "message": "No se pudo determinar el evento de la reservación"}
        )
    
    # Lista de errores para reportar qué categorías no alcanzan cupo
    detalles_error = []

    # Validar cupo por cada tipo de boleto incluido en la reservación
    for item in items:
        # Obtener el tipo de boleto (precio y cupo)
        tipo = db.query(TipoBoleto).filter(
            TipoBoleto.id_tipo_boleto == item.ticket_type_id
        ).first()

        # Si el tipo no existe, es un problema de datos/validación
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
        # join con Reservacion para filtrar solo estado PAGADA
        # se cuenta cuántos boletos ya están vendidos
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

        # Disponibles = cupo total - vendidos
        disponibles = int(tipo.cupo) - int(vendidos)

        # Si la reservación pide más de lo disponible, se junta en details para el 409
        if int(item.quantity) > disponibles:
            detalles_error.append({
                "ticket_type_id": item.ticket_type_id,
                "requested": int(item.quantity),
                "available": max(0, int(disponibles))
            })

    # Si al menos una categoría no alcanza, no se paga y se devuelve 409
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
    # cambia estado a PAGADA
    # registra paid_at en UTC (sin microsegundos)
    reservacion.estado = EstadoReservacion.PAGADA
    reservacion.paid_at = datetime.now(timezone.utc).replace(microsecond=0)

    # Guardar cambios en BD
    db.commit()
    db.refresh(reservacion)

    # Calcular total de la reservación:
    # Total = suma del precio por cada boleto (una fila por boleto)
    total = (
        db.query(func.sum(TipoBoleto.precio))
        .join(Boleto, Boleto.id_tipo_boleto == TipoBoleto.id_tipo_boleto)
        .filter(Boleto.id_reservacion == id_reservacion)
        .scalar()
    ) or 0

    # Respuesta final con status, paid_at y totals
    return {
        "id": reservacion.id_reservacion,
        "status": reservacion.estado.value,
        "paid_at": reservacion.paid_at.isoformat(),
        "totals": {"currency": "MXN", "total": float(total)}
    }

# 5.2 Cancelar reservación
# POST /reservations/{id_reservacion}/cancel

# Si está CREADA: cambia a CANCELADA y guarda canceled_at
# Si está PAGADA: prohíbe cancelación (409)
# Si no existe: 404
@enrutador.post("/{id_reservacion}/cancel")
def cancelar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    reservacion = db.query(Reservacion).filter(
        Reservacion.id_reservacion == id_reservacion
    ).first()

    # Si no existe, 404 con error JSON consistente
    if not reservacion:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "NOT_FOUND", "message": "No se encontró la reservación"}
        )

    # Si está PAGADA, no se puede cancelar
    if reservacion.estado == EstadoReservacion.PAGADA:
        raise HTTPException(
            status_code=409,
            detail={"error_code": "INVALID_STATE", "message": "No se puede cancelar una reservación pagada"}
        )
    
    # Si ya estaba cancelada, se devuelve el estado actual (no se modifica)
    if reservacion.estado == EstadoReservacion.CANCELADA:
        return {
            "id": reservacion.id_reservacion,
            "status": reservacion.estado.value,
            "canceled_at": reservacion.cancelada_en.isoformat()
        }

    # Cancelar:
    # cambia estado a CANCELADA
    # registra cancelada_en en UTC (sin microsegundos)
    reservacion.estado = EstadoReservacion.CANCELADA
    reservacion.cancelada_en = datetime.now(timezone.utc).replace(microsecond=0)

    # Guardar cambios en BD
    db.commit()
    db.refresh(reservacion)

    # Respuesta en el formato solicitado con canceled_at
    return {
        "id": reservacion.id_reservacion,
        "status": reservacion.estado.value,
        "canceled_at": reservacion.cancelada_en.isoformat()
    }
