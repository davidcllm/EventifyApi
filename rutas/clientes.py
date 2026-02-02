from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from base_de_datos import obtener_db

enrutador = APIRouter(prefix="/clients", tags=["Clientes"])

@enrutador.post("/")
def crear_cliente(db: Session = Depends(obtener_db)):
    # 1.1 Crear cliente
    pass

@enrutador.get("/{id_cliente}")
def obtener_cliente(id_cliente: int, db: Session = Depends(obtener_db)):
    # 1.2 Obtener cliente
    pass