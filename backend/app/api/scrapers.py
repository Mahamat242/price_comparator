import asyncio
from typing import Dict, Any
from fastapi import APIRouter, BackgroundTasks, status

from app.db.database import AsyncSessionLocal
from app.services.scraperServices import ScraperService

router = APIRouter()


async def _run_scraper(scraper_name: str):
    """ ouvre une nouvelle session DB indépendante du cycle de vie de la requête """
    async with AsyncSessionLocal() as db:
        service = ScraperService(db)
        if scraper_name == "jumia":
            await service.run_jumia()
        elif scraper_name == "expat_dakar":
            await service.run_expat_dakar()
        elif scraper_name == "all":
            await asyncio.gather(
                service.run_jumia(),
                service.run_expat_dakar(),
                return_exceptions=True
            )


@router.post("/jumia", status_code=status.HTTP_202_ACCEPTED)
async def scrape_jumia(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """ déclenche le scraping de Jumia en arrière-plan """
    background_tasks.add_task(_run_scraper, "jumia")
    return {
        "status": "pending",
        "message": "le scraping de Jumia a été lancé en arrière-plan"
    }


@router.post("/expat-dakar", status_code=status.HTTP_202_ACCEPTED)
async def scrape_expat_dakar(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """ déclenche le scraping de Expat Dakar en arrière-plan """
    background_tasks.add_task(_run_scraper, "expat_dakar")
    return {
        "status": "pending",
        "message": "le scraping de Expat Dakar a été lancé en arrière-plan"
    }


@router.post("/all", status_code=status.HTTP_202_ACCEPTED)
async def scrape_all(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """ déclenche le scraping parallèle de toutes les sources en arrière-plan """
    background_tasks.add_task(_run_scraper, "all")
    return {
        "status": "pending",
        "message": "le scraping global a été lancé en arrière-plan"
    }