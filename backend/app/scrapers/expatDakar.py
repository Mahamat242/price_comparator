import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Any, Dict
from app.scrapers.base import Base

logger = logging.getLogger(__name__)

class ExpatDakar(Base):
    def __init__(self):
        super().__init__(baseUrl="https://www.expat-dakar.com/")

    def data_extraction(self, categorie: str, soupCategoriePage: BeautifulSoup) -> List[Dict[str, Any]]:
        divArticles = soupCategoriePage.find('div', class_='listings-cards__list')
        if not divArticles:
            print(f"expat dakar : pas de div d'articles pour la catégorie : {categorie}")
            return []
        
        articles = divArticles.find_all('a', class_='cars-listing-card__inner listing-card__inner')
        data = []
        
        for i in articles:
            title_tag = i.find('div', class_='listing-card__header__title')
            price_tag = i.find('div', class_='listing-card__info-bar__price')
            imgTag = i.find('img')

            # protection contre les balises manquantes
            if not title_tag or not price_tag:
                continue

            title = title_tag.get_text(strip=True)
            price = self.clean_price(price_tag.get_text(strip=True))
            productUrl = self.url_construct(i.get('href'))
            
            # gestion des images lazy-loading d'expat dakar
            imageUrl = None
            if imgTag:
                imageUrl = imgTag.get('data-src') or imgTag.get('src') or imgTag.get('data-srcset')

            data.append(
                {
                    'title': title,
                    'price': price,
                    'category': categorie,
                    'source': 'Expat Dakar',
                    'product_url': productUrl,
                    'image_url': imageUrl,
                }
            )
        return data

    async def main(self) -> List[Dict[str, Any]]:
        # utilisation d'un client unique pour l'ensemble des requêtes du scraper
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
            htmlContent = await self.fetch_page(self.baseUrl, client=client)
            if not htmlContent: return []

            soup = BeautifulSoup(htmlContent, "html.parser")
            data = []

            # recherche des catégories
            divCat = soup.find('div', class_='tw-hero-categories-track')
            if divCat:
                cat = divCat.find_all('a', class_='tw-hero-icon')
                catLinks = self.categorie_links(cat)

                for item in catLinks:
                    htmlContentCategorie = await self.fetch_page(item['url'], client=client)
                    if not htmlContentCategorie: continue
                    soupCategoriePage = BeautifulSoup(htmlContentCategorie, 'html.parser')

                    # extraction des articles de la première page
                    data.extend(self.data_extraction(item['categorie'], soupCategoriePage))

                    # parcourir la pagination
                    page = 0
                    currentSoup = soupCategoriePage

                    while page < 2:
                        divPage = currentSoup.find('ul', class_='pagination')
                        if not divPage: break

                        nextPage = divPage.find('a', class_='page-link', attrs={'rel': 'next'}) or divPage.find('a', class_='page-link', attrs={'aria-label': 'Suivant »'})
                        if not nextPage or not nextPage.get('href'): break

                        # chargement de la page suivante
                        htmlContentPagination = await self.fetch_page(self.url_construct(nextPage.get('href')), client=client)
                        if not htmlContentPagination: break

                        currentSoup = BeautifulSoup(htmlContentPagination, 'html.parser')
                        data.extend(self.data_extraction(item['categorie'], currentSoup))
                        
                        page += 1

            return data