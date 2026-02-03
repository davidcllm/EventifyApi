import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

#Obtener los valores del connection string desde el .env
user = os.getenv("DB_USER", "postgres")
password = quote_plus(os.getenv("DB_PASSWORD"))
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

# Construcción del string de conexión.
DATABASE_URL = (
    f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
)

#Se crea el engine de sqlAlchemy, que se encarga de manejar la conexión a base de datos.
motor = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

# Es la base para todos los modelos ORM.
Base = declarative_base()

# Este fragmento crea una sesión por request, la inyecta en los endpoints, la cierra siempre,
# incluso si hay error.
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
