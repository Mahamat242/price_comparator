import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
import app.db.models as models
from app.api.products import router as productsRouter
from app.api.scrapers import router as scrapersRouter

# configuration du logging — affiche tous les messages info dans le terminal pour le debug et le suivi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

# création automatique des tables de façon asynchrone au démarrage de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(
    title="Price Comparator API",
    description="API d'extraction et de comparaison de prix pour les sites Jumia et Expat Dakar",
    version="1.0.0",
    lifespan=lifespan
)

# configuration du CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# inclusion des routeurs API
app.include_router(productsRouter, prefix="/api/products", tags=["Products"])
app.include_router(scrapersRouter, prefix="/api/scrapers", tags=["Scrapers"])

@app.get("/")
def read_root():
    return {"message": "api de comparaison de prix fonctionnelle !"}