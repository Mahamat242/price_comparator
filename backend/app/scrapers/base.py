import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Any, List
import httpx
from urllib.parse import urljoin
from pathlib import Path

class Base:
    def __init__(self, baseUrl : str):
        self.baseUrl = baseUrl
        self.headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"}

    def clean_price(self, lettre : str) -> float:
        """ méthode pour nettoyer les prix """

        if not lettre : return 0.0

        price = re.sub(r"[^\d]", "", lettre)
        return float(price) if price else 0.0

    async def fetch_page(self, url: str) -> Optional[str]:
        """ effectue un requet http  vers le site de façons asynchrone """
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
                return None
        except Exception as e:
            print(f"Erreur http lors de l'accès à {url} : {e}")

    def url_construct(self, url : str) -> str:
        return urljoin(self.baseUrl, url)

    def categorie_links(self, cat : any) -> List[Dict[str, str]]:
        if not cat: return []
        return [
            {
                "categorie" : i.get_text(strip=True),
                "url" : self.url_construct(i.get("href"))
            }
            for i in cat if i.get("href")
        ]