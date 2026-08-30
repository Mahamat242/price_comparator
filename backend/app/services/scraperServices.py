import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Product
from app.scrapers.jumia import Jumia
from app.scrapers.expatDakar import ExpatDakar

logger = logging.getLogger(__name__)


class ScraperService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_products(self, products_data: List[Dict[str, Any]]) -> int:
        new_count = 0
        updated_count = 0

        for item in products_data:
            product_url = item.get("product_url")
            if not product_url:
                continue

            # requête select asynchrone pour vérifier si le produit existe déjà en bd
            stmt = select(Product).where(Product.product_url == product_url)
            result = await self.db.execute(stmt)
            existing_product = result.scalars().first()

            if existing_product:
                if existing_product.price != item.get("price"):
                    existing_product.price = item.get("price")
                    updated_count += 1
            else:
                new_product = Product(
                    title=item.get("title"),
                    price=item.get("price"),
                    description=item.get("description"),
                    category=item.get("category"),
                    currency=item.get("currency", "FCFA"),
                    source=item.get("source"),
                    product_url=product_url,
                    image_url=item.get("image_url"),
                    metadata_info=item.get("metadata_info")
                )
                self.db.add(new_product)
                new_count += 1

        try:
            await self.db.commit()
            logger.info(f"succès bd : {new_count} nouveaux produits ajoutés, {updated_count} prix mis à jour")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Erreur d'enregistrement BDD : {e}")
            raise e

        return new_count

    async def run_jumia(self) -> Dict[str, Any]:
        scraper = Jumia()
        extracted_data = await scraper.main()
        saved_count = await self.save_products(extracted_data)
        logger.info(f"[jumia] terminé : {len(extracted_data)} extraits, {saved_count} enregistrés")
        return {"total_extracted": len(extracted_data), "total_saved": saved_count}

    async def run_expat_dakar(self) -> Dict[str, Any]:
        scraper = ExpatDakar()
        extracted_data = await scraper.main()
        saved_count = await self.save_products(extracted_data)
        logger.info(f"[expat dakar] terminé : {len(extracted_data)} extraits, {saved_count} enregistrés")
        return {"total_extracted": len(extracted_data), "total_saved": saved_count}