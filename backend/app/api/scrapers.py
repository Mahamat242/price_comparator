import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.scraperServices import ScraperService

router = APIRouter()


@router.post("/jumia")
async def scrape_jumia(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    service = ScraperService(db)
    result = await service.run_jumia()
    return {"status": "success", "source": "Jumia", "details": result}


@router.post("/expat-dakar")
async def scrape_expat_dakar(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    service = ScraperService(db)
    result = await service.run_expat_dakar()
    return {"status": "success", "source": "Expat Dakar", "details": result}


@router.post("/all")
async def scrape_all(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    service = ScraperService(db)
    
    # lancer des 2 scrapers en parallèle
    jumia_res, expat_res = await asyncio.gather(
        service.run_jumia(),
        service.run_expat_dakar(),
        return_exceptions=True
    )

    return {
        "status": "success",
        "results": {
            "jumia": jumia_res if not isinstance(jumia_res, Exception) else str(jumia_res),
            "expat_dakar": expat_res if not isinstance(expat_res, Exception) else str(expat_res)
        }
    }