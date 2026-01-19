from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv
import logging
import cloudscraper
from typing import Optional, Dict, Any

load_dotenv()

logger = logging.getLogger(__name__)

class Parsing:
    def __init__(self) -> None:
        # Gunakan domain terbaru .moe
        self.url: str = "https://anichin.moe"
        self.history_url: Optional[str] = None
        
        # Inisialisasi cloudscraper dengan konfigurasi browser chrome
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        logger.info(f"Initialized Parsing session with URL: {self.url}")

    def __get_html(self, slug: str, **kwargs: Any) -> Optional[str]:
        try:
            # Pastikan URL terbentuk dengan benar
            clean_slug = slug.lstrip('/')
            url = f"{self.url}/{clean_slug}" if clean_slug else self.url

            # Headers lengkap untuk mengelabui Cloudflare
            headers: Dict[str, str] = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://anichin.moe/",
                "Origin": "https://anichin.moe",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Connection": "keep-alive",
            }

            if kwargs.get("headers"):
                headers.update(kwargs["headers"])
            
            logger.debug(f"Making request to: {url}")
            
            # Melakukan request menggunakan cloudscraper
            response = self.scraper.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                self.history_url = url
                return response.text
            else:
                logger.error(f"Failed to fetch HTML. Status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching HTML: {e}")
            return None

    def get_parsed_html(self, url: str, **kwargs: Any) -> Optional[BeautifulSoup]:
        html_content = self.__get_html(url, **kwargs)
        if html_content:
            return BeautifulSoup(html_content, "html.parser")
        return None

    def parsing(self, data: str) -> Optional[BeautifulSoup]:
        if not data: return None
        return BeautifulSoup(data, "html.parser")
