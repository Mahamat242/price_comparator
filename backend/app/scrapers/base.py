import re
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Base:
    def __init__(self, baseUrl: str):
        self.baseUrl = baseUrl
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def clean_price(self, lettre: str) -> float:
        """ méthode pour nettoyer les prix """

        if not lettre: return 0.0

        price = re.sub(r"[^\d]", "", lettre)
        return float(price) if price else 0.0

    async def fetch_page(self, url: str, client: Optional[httpx.AsyncClient] = None) -> Optional[str]:
        """ effectue un requet http  vers le site de façons asynchrone """
        try:
            # réutilisation du client s'il est fourni, sinon création d'une session temporaire
            if client:
                response = await client.get(url, headers=self.headers, follow_redirects=True, timeout=10.0)
                if response.status_code == 200:
                    return response.text
                return None
            else:
                async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=10.0) as temp_client:
                    response = await temp_client.get(url)
                    if response.status_code == 200:
                        return response.text
                    return None
        except Exception as e:
            # enregistrement des erreurs d'accès réseau
            logger.error(f"Erreur http lors de l'accès à {url} : {e}")
            print(f"Erreur http lors de l'accès à {url} : {e}")
            return None

    async def fetch_soup(self, url: str, client: Optional[httpx.AsyncClient] = None) -> Optional[BeautifulSoup]:
        """ 
            récupère le contenu html d'une page et le transforme en objet beautifulsoup 
        """
        html = await self.fetch_page(url, client=client)
        if html:
            return BeautifulSoup(html, "html.parser")
        return None

    def url_construct(self, url: str) -> str:
        return urljoin(self.baseUrl, url)

    def categorie_links(self, cat: Any) -> List[Dict[str, str]]:
        if not cat: return []
        return [
            {
                "categorie": i.get_text(strip=True),
                "url": self.url_construct(i.get("href"))
            }
            for i in cat if i.get("href")
        ]