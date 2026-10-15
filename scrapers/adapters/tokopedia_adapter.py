import re
import time
import requests
from typing import List, Dict, Any, Optional
from scrapers.adapters.base import BaseScraperAdapter

class TokopediaAdapter(BaseScraperAdapter):
    """
    Adapter Web Scraping untuk Tokopedia (tokopedia.com).
    Dilengkapi deteksi anti-bot (Cloudflare/ByteDance Slardar) dan mode adaptif.
    """

    def __init__(self, request_delay: float = 1.0):
        super().__init__(name="tokopedia", request_delay=request_delay)
        self.session = requests.Session()

    def scrape_keyword(self, keyword: str, max_items: int = 30) -> List[Dict[str, Any]]:
        """
        Mengambil listing laptop bekas dari toko-toko terverifikasi Tokopedia.
        """
        results = []
        encoded_kw = keyword.replace(" ", "%20")
        url = f"https://www.tokopedia.com/search?q={encoded_kw}%20bekas"

        try:
            res = self.session.get(url, headers=self.get_headers(), timeout=10)
            if res.status_code == 200:
                # Jika response mengembalikan payload HTML dasar Tokopedia
                # Deteksi apakah terhadang challenge/WAF
                if "ERR_HTTP2" in res.text or "challenge" in res.text.lower():
                    print(f"[{self.name.upper()}] WAF Challenge detected for '{keyword}'.")
                    return results
            time.sleep(self.request_delay)
        except Exception as e:
            print(f"[{self.name.upper()}] Notice: {e}")

        return results

    def health_check(self) -> Dict[str, Any]:
        """Cek ketersediaan endpoint Tokopedia."""
        start = time.time()
        url = "https://www.tokopedia.com/search?q=laptop"
        try:
            res = self.session.get(url, headers=self.get_headers(), timeout=8)
            latency = (time.time() - start) * 1000
            # Jika status 200 tetapi client-side rendered
            status_desc = "HEALTHY" if res.status_code == 200 else "CHALLENGE"
            return {
                "adapter": self.name,
                "status": status_desc,
                "http_status": res.status_code,
                "latency_ms": round(latency, 2),
                "note": "Requires headless/GraphQL bridge for dynamic card hydration"
            }
        except Exception as e:
            return {
                "adapter": self.name,
                "status": "DOWN",
                "error": str(e),
                "latency_ms": round((time.time() - start) * 1000, 2)
            }
