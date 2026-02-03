from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from base_de_datos import obtener_db
from modelos import Cliente

enrutador = APIRouter(prefix="/clients", tags=["Clientes"])

# 1.1 Crear cliente
@enrutador.post("/", status_code=201)
def crear_cliente(payload: dict, db: Session = Depends(obtener_db)):
    for field in ("name", "email", "phone"):
        if field not in payload or not str(payload[field]).strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": f"missing field {field}",
                    "details": {"field": field}
                }
            )

    cliente = Cliente(
        nombre=payload["name"].strip(),
        correo=payload["email"].strip(),
        telefono=payload["phone"].strip(),
        created_at=datetime.now(timezone.utc)
    )

    db.add(cliente)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "VALIDATION_ERROR",
                "message": "email already exists",
                "details": {"field": "email"}
            }
        )

    db.refresh(cliente)

    return {
        "id": str(cliente.id_cliente),
        "name": cliente.nombre,
        "email": cliente.correo,
        "phone": cliente.telefono,
        "created_at": cliente.created_at.isoformat().replace("+00:00", "Z")
    }

# 1.2 Obtener cliente
@enrutador.get("/{id_cliente}", status_code=200)
def obtener_cliente(id_cliente: int, db: Session = Depends(obtener_db)):
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "NOT_FOUND",
                    "message": "client not found"
                }
            )

        return {
            "id": str(cliente.id_cliente),
            "name": cliente.nombre,
            "email": cliente.correo,
            "phone": cliente.telefono,
            "created_at": cliente.created_at.isoformat().replace("+00:00", "Z")
        }