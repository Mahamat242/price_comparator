from fastapi import FastAPI
from app.db.database import engine
import app.db.models as models
from fastapi.middleware.cors import CORSMiddleware

# pour dire à pg de créer la table si elle n'existe pas encore
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title= "Price Comparator API",
    description="API d'extraction et de comparaison de prix pour les sites Jumia et Expat Dakar",
    version= "1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message : " : "api de comparaison de prix fonctionnelle !"}