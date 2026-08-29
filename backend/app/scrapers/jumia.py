from bs4 import BeautifulSoup
import requests
from app.scrapers.base import Base
from typing import List, Any, Dict

class Jumia(Base):
    def __init__(self):
        super().__init__(baseUrl = "https://www.jumia.sn/")

    def data_extraction(self, categorie, soupCategoriePage) -> List[Dict[str, Any]]:
        divArticles = soupCategoriePage.find('div', class_='-phm -pvxs row _no-g _4cl-3cm-shs')
        if not divArticles: 
            print(f"jumia : pas de div d'articles pour la catégorie : {categorie}")
            return []
        articles = divArticles.find_all('article', class_='prd _fb col c-prd')
        data = []
        for i in articles:
            title_tag = i.find('h3', class_='name')
            price_tag = i.find('div', class_='prc')
            category = categorie
            productUrl_tag = i.find('a', class_='core')
            imgTag = i.find('img', class_='img')

            # protection contre les balises manquantes
            if not title_tag or not price_tag or not productUrl_tag:
                continue

            title = title_tag.get_text(strip=True)
            price = self.clean_price(price_tag.get_text(strip=True))
            productUrl = self.url_construct(productUrl_tag.get('href'))
            imageUrl = (imgTag.get('data-src') or imgTag.get('src')) if imgTag else None

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

    async def main(self) -> List[Dict[str, Any]]:
        htmlContent = await self.fetch_page(self.baseUrl)
        if not htmlContent : return []

        soup = BeautifulSoup(htmlContent, "html.parser")
        data = []

        # recheche des catégories
        divCat = soup.find('div', class_="crs")
        if divCat:
            cat = divCat.find_all('a', class_="cat-bar-itm")
            catLinks = self.categorie_links(cat)

            for item in catLinks:
                htmlContentCategorie = await self.fetch_page(item['url'])
                if not htmlContentCategorie: continue
                soupCategoriePage = BeautifulSoup(htmlContentCategorie, 'html.parser')

                # extraction des articles de la première page
                data.extend(self.data_extraction(item['categorie'], soupCategoriePage))                

                # parcourir la paignation
                page = 0 # pour limiter l'itération à 3 pages
                currentSoup = soupCategoriePage
                
                while page < 2:
                    divPage = currentSoup.find('div', class_='pg-w -ptxl -pbxxxl')
                    if not divPage: break

                    nextPage = divPage.find('a', class_='pg', attrs={'aria-label' : 'Page suivante'})
                    if not nextPage or not nextPage.get('href'): break

                    # chargement de la page suivante
                    htmlContentPagination = await self.fetch_page(self.url_construct(nextPage.get('href')))
                    if not htmlContentPagination: break

                    currentSoup = BeautifulSoup(htmlContentPagination, 'html.parser')
                    data.extend(self.data_extraction(item['categorie'], currentSoup))
                    
                    page += 1

        return data