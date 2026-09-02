import logging
from bs4 import BeautifulSoup
from typing import List, Any, Dict
from curl_cffi.requests import AsyncSession
from app.scrapers.base import Base

logger = logging.getLogger(__name__)

class Jumia(Base):
    def __init__(self):
        super().__init__(baseUrl="https://www.jumia.sn/")

    def data_extraction(self, categorie: str, soupCategoriePage: BeautifulSoup) -> List[Dict[str, Any]]:
        # extraction des articles
        articles = soupCategoriePage.find_all('article', class_=lambda c: c and 'prd' in c)
        if not articles:
            logger.warning(f"[Jumia] div articles introuvable pour la catégorie : '{categorie}' — la structure HTML a peut-être changé")
            return []

        data = []

        for i in articles:
            title_tag = i.find(class_='name')
            price_tag = i.find(class_='prc')
            productUrl_tag = i.find('a', class_='core') or i.find('a', href=True)
            imgTag = i.find('img', class_='img') or i.find('img')

            # verifie les champs obligatoires
            if not title_tag or not price_tag or not productUrl_tag:
                continue

            title = title_tag.get_text(strip=True)
            price = self.clean_price(price_tag.get_text(strip=True))
            productUrl = self.url_construct(productUrl_tag.get('href'))
            
            # image avec lazy loading
            imageUrl = None
            if imgTag:
                imageUrl = imgTag.get('data-src') or imgTag.get('src') or imgTag.get('data-lazy-src')

            data.append(
                {
                    'title': title,
                    'price': price,
                    'category': categorie,
                    'source': 'Jumia',
                    'product_url': productUrl,
                    'image_url': imageUrl,
                }
            )
        return data

    def extract_categories_from_home(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        # categories accueil
        categories = []
        for a in soup.find_all('a', class_='col'):
            href = a.get('href')
            text = a.get_text(strip=True)
            if href and text:
                categories.append({
                    "categorie": text,
                    "url": self.url_construct(href)
                })

        if not categories:
            flyout = soup.find('div', class_='flyout') or soup.find('div', class_='crs')
            if flyout:
                for a in flyout.find_all('a'):
                    href = a.get('href')
                    text = a.get_text(strip=True)
                    if href and text:
                        categories.append({
                            "categorie": text,
                            "url": self.url_construct(href)
                        })

        return categories

    async def main(self) -> List[Dict[str, Any]]:
        logger.info("[Jumia] début du scraping...")
        # session client partagee
        async with AsyncSession(impersonate="chrome124", headers=self.headers) as client:
            htmlContent = await self.fetch_page(self.baseUrl, client=client)
            if not htmlContent:
                logger.error("[Jumia] impossible de charger la page d'accueil")
                return []

            soup = BeautifulSoup(htmlContent, "html.parser")
            data = []

            # recupere les categories
            catLinks = self.extract_categories_from_home(soup)
            if not catLinks:
                divCat = soup.find('div', class_="crs")
                if divCat:
                    cat = divCat.find_all('a', class_="cat-bar-itm")
                    catLinks = self.categorie_links(cat)

            logger.info(f"[Jumia] {len(catLinks)} catégories trouvées")

            for item in catLinks:
                logger.info(f"[Jumia] scraping de la catégorie : {item['categorie']} ({item['url']})")
                htmlContentCategorie = await self.fetch_page(item['url'], client=client)
                if not htmlContentCategorie: continue
                soupCategoriePage = BeautifulSoup(htmlContentCategorie, 'html.parser')

                # premiere page
                data.extend(self.data_extraction(item['categorie'], soupCategoriePage))

                # pagination
                page = 0 # limite a 2 pages
                currentSoup = soupCategoriePage
                
                while page < 2:
                    divPage = currentSoup.find('div', class_='pg-w -ptxl -pbxxxl')
                    if not divPage: break

                    nextPage = divPage.find('a', class_='pg', attrs={'aria-label': 'Page suivante'})
                    if not nextPage or not nextPage.get('href'): break

                    # page suivante
                    htmlContentPagination = await self.fetch_page(self.url_construct(nextPage.get('href')), client=client)
                    if not htmlContentPagination: break

                    currentSoup = BeautifulSoup(htmlContentPagination, 'html.parser')
                    data.extend(self.data_extraction(item['categorie'], currentSoup))
                    
                    page += 1

            logger.info(f"[Jumia] scraping terminé — {len(data)} produits extraits au total")
            return data