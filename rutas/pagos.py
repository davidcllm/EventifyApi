from modelos import Reservacion, EstadoReservacion
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from base_de_datos import obtener_db


enrutador = APIRouter(prefix="/reservations", tags=["Pagos y Cancelaciones"])

@enrutador.post("/{id_reservacion}/pay")
def pagar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    # 5.1 Pagar (Validar cupos y cambiar estado a PAGADA)
    pass

@enrutador.post("/{id_reservacion}/cancel")
def cancelar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    # 5.2 Cancelar reservación
    
    reservacion = db.query(Reservacion).filter(Reservacion.id_reservacion == id_reservacion).first()

    # Si no hay reservación
    if not reservacion:
        raise HTTPException(status_code=404, detail="No se encontró la reservación")

    # Si ya está pagada
    if reservacion.estado == EstadoReservacion.PAGADA:
        raise HTTPException(status_code=409, detail="No se puede cancelar una reservación pagada")
    
    # Si ya está cancelada
    if reservacion.estado == EstadoReservacion.CANCELADA:
        
        return {
            "id": reservacion.id_reservacion,
            "status": reservacion.estado.value,  
            "cancelada_en": reservacion.cancelada_en.isoformat()
        }

    # Si está creada
    reservacion.estado = EstadoReservacion.CANCELADA
    reservacion.cancelada_en = datetime.now(timezone.utc).replace(microsecond=0)
    db.commit()
    db.refresh(reservacion)
    
    return {
        "id": reservacion.id_reservacion,
        "status": reservacion.estado.value,  
        "cancelada_en": reservacion.cancelada_en.isoformat()
    }





