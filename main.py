from fastapi import FastAPI
from base_de_datos import motor, Base
from rutas import clientes, eventos, tipos_boleto, reservaciones, pagos

# Crea las tablas al iniciar
Base.metadata.create_all(bind=motor)

app = FastAPI(title="Eventify API")

# Registrar los módulos (routers)
app.include_router(clientes.enrutador)
app.include_router(eventos.enrutador)
app.include_router(tipos_boleto.enrutador)
app.include_router(reservaciones.enrutador)
app.include_router(pagos.enrutador)

# endpoint demo
@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a Eventify"}