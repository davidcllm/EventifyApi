from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from base_de_datos import obtener_db

enrutador = APIRouter(prefix="/reservations", tags=["Reservaciones"])

@enrutador.post("/")
def crear_reservacion(db: Session = Depends(obtener_db)):
    # 4.1 Crear reservación
    pass

@enrutador.put("/{id_reservacion}/items")
def actualizar_item_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    # 4.2 Agregar o actualizar ítem (Solo si estado es CREADA)
    pass

@enrutador.delete("/{id_reservacion}/items/{id_tipo_boleto}")
def eliminar_item_reservacion(id_reservacion: int, id_tipo_boleto: int, db: Session = Depends(obtener_db)):
    # 4.3 Eliminar ítem de reservación
    pass

@enrutador.get("/{id_reservacion}")
def consultar_reservacion(id_reservacion: int, db: Session = Depends(obtener_db)):
    # 4.4 Consultar reservación con items
    pass