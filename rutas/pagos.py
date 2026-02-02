from fastapi import APIRouter, Depends
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
    pass