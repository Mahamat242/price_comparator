from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# lien de connexion vers le conteneur Docker PostgreSQL
DATABASE_URL = "postgresql://pc_user:pc_password@localhost:5432/pc_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# fonction pour ouvrir ou fermé la connexion à la bd lors des requêtes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()