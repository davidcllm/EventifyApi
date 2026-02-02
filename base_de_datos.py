import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

contrasena_segura = quote_plus(os.getenv("DB_PASSWORD"))
nombre_db = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://postgres:{contrasena_segura}@localhost:5432/{nombre_db}"

motor = create_engine(DATABASE_URL)
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()

def obtener_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()