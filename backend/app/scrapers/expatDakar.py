from bs4 import BeautifulSoup
import requests
from app.scrapers.base import Base
from typing import List, Any, Dict

class ExpatDakar(Base):
    def __init__(self):
            super().__init__(baseUrl = "https://www.expat-dakar.com/")

    def data_extraction(self, categorie, soupCategoriePage) -> List[Dict[str, Any]]:
        divArticles = soupCategoriePage.find('div', class_='listings-cards__list')
        if not divArticles:
            print(f"expat dakar : pas de div d'articles pour la catégorie : {categorie}")
            return []
        articles = divArticles.find_all('div', class_='listings-cards__list-item ')
        data = []
        for i in articles:
            title_tag = i.find('div', class_='listing-card__header__title')
            price_tag = i.find('div', class_='listing-card__info-bar__price')
            category = categorie
            productUrl_tag = i.find('a', class_='listing-card__inner')
            imgTag = i.find('img', class_='listing-card__image__resource vh-img')

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

          # recherche des catégories
        divCat = soup.find('div', class_='tw-hero-categories-track')
        if divCat :
            cat = divCat.find_all('a', class_='tw-hero-icon')
            catLinks = self.categorie_links(cat)

            for item in catLinks:
                htmlContentCategorie = await self.fetch_page(item['url'])
                if not htmlContentCategorie: continue
                soupCategoriePage = BeautifulSoup(htmlContentCategorie, 'html.parser')

                # extraction des articles
                data.extend(self.data_extraction(item['categorie'], soupCategoriePage))

                # parcourir la pagination
                page = 0
                currentSoup = soupCategoriePage

                while page < 2:
                    divPage = currentSoup.find('ul', class_='pagination')
                    if not divPage: break

                    nextPage = divPage.find('a', class_='page-link', attrs={'aria-label' : 'Suivant »'})
                    if not nextPage or not nextPage.get('href'): break

                    # chargement de la page suivante
                    htmlContentPagination = await self.fetch_page(self.url_construct(nextPage.get('href')))
                    if not htmlContentPagination: break

                    currentSoup = BeautifulSoup(htmlContentPagination, 'html.parser')
                    data.extend(self.data_extraction(item['categorie'], currentSoup))
                    
                    page += 1

        return data
