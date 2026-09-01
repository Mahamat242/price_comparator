import logging
from bs4 import BeautifulSoup
from typing import List, Any, Dict
from curl_cffi.requests import AsyncSession
from app.scrapers.base import Base

logger = logging.getLogger(__name__)


class ExpatDakar(Base):
    def __init__(self):
        super().__init__(baseUrl="https://www.expat-dakar.com/")

    def data_extraction(self, categorie: str, soupCategoriePage: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extrait les informations des annonces d'une page de catégorie """
        articles = soupCategoriePage.find_all('div', class_='listing-card')
        if not articles:
            logger.warning(f"[ExpatDakar] Aucun article trouvé pour la catégorie : '{categorie}'")
            return []

        data = []

        for item in articles:
            title_tag = item.find('div', class_='listing-card__header__title')
            price_tag = (
                item.find('span', class_='listing-card__price__value') or
                item.find('div', class_='listing-card__info-bar__price') or
                item.find(class_=lambda x: x and 'price' in x)
            )
            url_tag = item.find('a', class_='listing-card__inner') or item.find('a', href=True)
            img_tag = item.find('img')

            # protection contre les balises obligatoires manquantes
            if not title_tag or not url_tag:
                continue

            raw_href = url_tag.get('href')
            if not raw_href:
                continue

            title = title_tag.get_text(strip=True)
            price = self.clean_price(price_tag.get_text(strip=True)) if price_tag else 0.0
            product_url = self.url_construct(raw_href)

            # gestion des images lazy-loading
            image_url = None
            if img_tag:
                image_url = (
                    img_tag.get('data-src') or
                    img_tag.get('src') or
                    img_tag.get('data-lazy-src') or
                    img_tag.get('data-srcset')
                )

            data.append({
                'title': title,
                'price': price,
                'category': categorie,
                'source': 'Expat Dakar',
                'product_url': product_url,
                'image_url': image_url,
            })

        return data

    async def main(self) -> List[Dict[str, Any]]:
        """Point d'entrée principal pour lancer le scraping d'Expat Dakar."""
        logger.info("[ExpatDakar] Début du scraping...")
        # utilisation d'un client unique pour l'ensemble des requêtes du scraper
        async with AsyncSession(impersonate="chrome124", headers=self.headers) as client:
            html_content = await self.fetch_page(self.baseUrl, client=client)
            if not html_content:
                logger.error("[ExpatDakar] Impossible de charger la page d'accueil")
                return []

            soup = BeautifulSoup(html_content, "html.parser")
            data = []

            # recherche des catégories
            div_cat = soup.find('div', class_='tw-hero-categories-track')
            if div_cat:
                cat = div_cat.find_all('a', class_='tw-hero-icon')
                cat_links = self.categorie_links(cat)
                logger.info(f"[ExpatDakar] {len(cat_links)} catégories trouvées")

                for item in cat_links:
                    html_content_categorie = await self.fetch_page(item['url'], client=client)
                    if not html_content_categorie:
                        logger.debug(f"[ExpatDakar] l'url suivant n'a pas abouti : {item['url']}")
                        continue
                    soup_categorie_page = BeautifulSoup(html_content_categorie, 'html.parser')

                    # extraction des articles de la première page
                    data.extend(self.data_extraction(item['categorie'], soup_categorie_page))

                    # parcourir la pagination
                    page = 0
                    current_soup = soup_categorie_page

                    while page < 2:
                        div_page = current_soup.find('ul', class_='pagination')
                        if not div_page:
                            break

                        next_page = (
                            div_page.find('a', class_='page-link', attrs={'rel': 'next'}) or
                            div_page.find('a', class_='page-link', attrs={'aria-label': 'Suivant »'})
                        )
                        if not next_page:
                            break
                        next_href = next_page.get('href')
                        if not next_href:
                            break

                        # chargement de la page suivante
                        html_content_pagination = await self.fetch_page(self.url_construct(next_href), client=client)
                        if not html_content_pagination:
                            break

                        current_soup = BeautifulSoup(html_content_pagination, 'html.parser')
                        data.extend(self.data_extraction(item['categorie'], current_soup))
                        page += 1

            logger.info(f"[ExpatDakar] Scraping terminé — {len(data)} produits extraits au total")
            return data