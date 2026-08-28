from fastapi import FastAPI
from backend.app.db.database import engine
import backend.app.db.models as models

# pour dire à pg de créer la table si elle n'existe pas encore
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title= "Price Comparator API")

@app.get("/")
def read_root():
    return {"message : " : "api de comparaison de prix fonctionnelle !"}