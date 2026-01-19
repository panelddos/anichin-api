from .parsing import Parsing
from urllib.parse import urlparse
import re
import logging
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

class Home(Parsing):
    def __init__(self, page: int = 1) -> None:
        super().__init__()
        self.__page: int = page

    def __get_card(self, item: Tag) -> Optional[Dict[str, Any]]:
        """Ekstrak data anime dari setiap elemen list."""
        try:
            # Selector terbaru Anichin menggunakan class 'bsx' atau langsung tag 'a'
            link_tag = item.find("a", href=True)
            if not link_tag: return None

            url = link_tag["href"]
            title = link_tag.get("title") or item.find("h2").text.strip()
            
            # Thumbnail (menangani lazy load)
            img_tag = item.find("img")
            thumbnail = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""

            # Episode & Type
            eps_tag = item.find("span", class_="epx")
            eps = eps_tag.text.strip() if eps_tag else "0"
            
            type_tag = item.find("span", class_="typez")
            anime_type = type_tag.text.strip() if type_tag else "Unknown"

            # Ambil slug dari URL
            slug = url.strip("/").split("/")[-1]

            return {
                "title": title,
                "type": anime_type,
                "eps": eps,
                "thumbnail": thumbnail,
                "slug": slug,
                "url": url
            }
        except Exception as e:
            logger.error(f"Error parse card: {e}")
            return None

    def __get_home(self, data: BeautifulSoup) -> Dict[str, Any]:
        """Mencari container utama pembungkus list anime."""
        cards = []
        try:
            # Anichin terbaru menggunakan class 'listupd' untuk daftar update terbaru
            container = data.find("div", class_="listupd")
            if not container:
                # Fallback ke bixbox jika di halaman tertentu berbeda
                container = data.find("div", class_="bixbox")

            if container:
                # Setiap anime biasanya dibungkus dalam class 'utimes', 'bs', atau 'article'
                items = container.find_all(["div", "article"], class_=["utimes", "bs", "bsx"])
                
                section_items = []
                for item in items:
                    card = self.__get_card(item)
                    if card:
                        section_items.append(card)
                
                if section_items:
                    cards.append({"section": "latest_update", "cards": section_items})

            return {
                "results": cards,
                "page": self.__page,
                "total": len(cards[0]["cards"]) if cards else 0,
                "source": self.history_url,
            }

        except Exception as e:
            logger.error(f"Error home content: {e}")
            return {"results": [], "error": str(e)}

    def get_details(self) -> Dict[str, Any]:
        try:
            # Jika halaman 1, url kosong (base url), jika > 1 gunakan path /page/
            url = f"/page/{self.__page}/" if self.__page > 1 else "/"
            
            data = self.get_parsed_html(url)
            if not data:
                return {"results": [], "error": "Failed to fetch HTML"}

            return self.__get_home(data)
        except Exception as e:
            return {"results": [], "error": str(e)}
