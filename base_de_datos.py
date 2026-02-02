import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

user = os.getenv("DB_USER", "postgres")
password = quote_plus(os.getenv("DB_PASSWORD"))
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
)

motor = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()

def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
