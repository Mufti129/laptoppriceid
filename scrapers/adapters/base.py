import abc
import random
from typing import List, Dict, Any, Optional

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
]

class BaseScraperAdapter(abc.ABC):
    """
    Interface Standar Adapter Marketplace untuk Ekosistem LaptopPrice ID.
    Setiap marketplace (Carousell, Tokopedia, Shopee, Pricebook) mengimplementasikan interface ini.
    """

    def __init__(self, name: str, request_delay: float = 0.5):
        self.name = name
        self.request_delay = request_delay

    def get_headers(self) -> Dict[str, str]:
        """Headers HTTP menyerupai browser desktop asli dengan parameter Client Hints."""
        return {
            "User-Agent": random.choice(DEFAULT_USER_AGENTS),
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Ch-Ua": '"Chromium";v="129", "Not=A?Brand";v="8", "Google Chrome";v="129"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

    @abc.abstractmethod
    def scrape_keyword(self, keyword: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """Mengambil daftar listing mentah untuk kata kunci pencarian tertentu."""
        pass

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Memeriksa apakah endpoint marketplace dapat diakses dan responsif."""
        pass
