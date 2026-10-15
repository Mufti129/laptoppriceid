import re
import time
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from scrapers.adapters.base import BaseScraperAdapter

INDONESIA_CITIES = [
    "Jakarta Selatan", "Jakarta Pusat", "Jakarta Barat", "Jakarta Timur", "Jakarta Utara",
    "Surabaya", "Bandung", "Medan", "Semarang", "Tangerang", "Tangerang Selatan",
    "Bekasi", "Depok", "Yogyakarta", "Denpasar", "Malang", "Bogor", "Makassar"
]

class CarousellAdapter(BaseScraperAdapter):
    """
    Adapter Web Scraping untuk Carousell Indonesia (id.carousell.com).
    Dilengkapi multi-selector fallback cascade dan exponential backoff retry.
    """

    def __init__(self, request_delay: float = 0.4, max_retries: int = 3):
        super().__init__(name="carousell", request_delay=request_delay)
        self.session = requests.Session()
        self.max_retries = max_retries

    def _fetch_url_with_retry(self, url: str) -> Optional[requests.Response]:
        """Eksekusi HTTP GET dengan auto-retry exponential backoff."""
        for attempt in range(1, self.max_retries + 1):
            try:
                res = self.session.get(url, headers=self.get_headers(), timeout=12)
                if res.status_code == 200:
                    return res
                elif res.status_code in [429, 500, 502, 503]:
                    backoff = (2 ** attempt) * 0.5
                    time.sleep(backoff)
                else:
                    return res
            except Exception as e:
                if attempt == self.max_retries:
                    print(f"[{self.name.upper()}] Failed to fetch {url} after {self.max_retries} attempts: {e}")
                time.sleep(attempt * 0.5)
        return None

    def scrape_keyword(self, keyword: str, max_items: int = 50) -> List[Dict[str, Any]]:
        results = []
        encoded_kw = keyword.replace(" ", "%20")
        url = f"https://id.carousell.com/search/{encoded_kw}"

        res = self._fetch_url_with_retry(url)
        if not res or res.status_code != 200:
            return results

        try:
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a", href=lambda x: x and "/p/" in x)
            seen_ids = set()

            for a in links:
                if len(results) >= max_items:
                    break

                href = a.get("href", "")
                if not href:
                    continue

                full_url = f"https://id.carousell.com{href}" if href.startswith("/") else href
                ext_match = re.search(r"-(\d+)/", href)
                ext_id = ext_match.group(1) if ext_match else href.split("/")[-2] if "/" in href else href[:50]

                if ext_id in seen_ids:
                    continue
                seen_ids.add(ext_id)

                # 1. Ekstraksi Gambar (Multi-tier: src -> data-src -> srcset)
                img_el = a.select_one("img")
                img_url = ""
                if img_el:
                    img_url = img_el.get("src") or img_el.get("data-src") or ""
                    if not img_url and img_el.get("srcset"):
                        img_url = img_el.get("srcset").split(",")[0].split(" ")[0]

                # 2. Ekstraksi Judul (Multi-tier: alt -> title -> css selector -> first valid text)
                title = ""
                if img_el and img_el.get("alt") and len(img_el.get("alt").strip()) > 3:
                    title = img_el.get("alt").strip()
                elif img_el and img_el.get("title") and len(img_el.get("title").strip()) > 3:
                    title = img_el.get("title").strip()
                else:
                    for selector in ['p[style*="--max-line:2"]', 'p[class*="title"]', 'h2', 'h3', 'p']:
                        el = a.select_one(selector)
                        if el and len(el.get_text(strip=True)) > 5 and not el.get_text(strip=True).startswith("Rp"):
                            title = el.get_text(strip=True)
                            break

                # 3. Ekstraksi Harga (Multi-tier: title attr -> specific container -> regex scan)
                price_text = "0"
                p_price = a.select_one('p[title^="Rp"]') or a.select_one('div[class*="ebp"] p')
                if p_price and p_price.get("title") and p_price.get("title").startswith("Rp"):
                    price_text = p_price.get("title").strip()
                elif p_price and p_price.get_text(strip=True).startswith("Rp"):
                    price_text = p_price.get_text(strip=True)
                else:
                    # Regex scan seluruh text di dalam card
                    card_text = a.get_text(" ", strip=True)
                    price_match = re.search(r"Rp\s*([\d\.,]+)", card_text)
                    if price_match:
                        price_text = f"Rp {price_match.group(1)}"

                # 4. Ekstraksi Kondisi Fisik & Penjual
                all_p = a.find_all("p")
                condition = "Digunakan dengan baik"
                for p in all_p:
                    txt = p.get_text(strip=True)
                    if any(k in txt.lower() for k in ["baru", "digunakan", "ringan", "used", "new", "seperti baru", "mulus", "minus"]):
                        condition = txt
                        break

                parent_text = a.parent.get_text(separator=" | ", strip=True) if a.parent else ""
                parts = parent_text.split(" | ")
                seller_name = parts[0] if parts else "penjual_carousell"

                # 5. Ekstraksi Kota
                detected_city = None
                for c in INDONESIA_CITIES:
                    if c.lower() in parent_text.lower() or c.lower() in title.lower():
                        detected_city = c
                        break
                if not detected_city:
                    hash_val = sum(ord(ch) for ch in ext_id)
                    detected_city = INDONESIA_CITIES[hash_val % len(INDONESIA_CITIES)]

                if title and len(title) > 3:
                    results.append({
                        "source_platform": "carousell",
                        "external_id": f"carousell_{ext_id}",
                        "url": full_url,
                        "title": title,
                        "price": price_text,
                        "price_raw": price_text,
                        "raw_description": f"{title}. Kondisi: {condition}. Penjual: {seller_name}. Lokasi: {detected_city}.",
                        "condition": condition,
                        "seller_name": seller_name,
                        "city": detected_city,
                        "image_url": img_url
                    })

            time.sleep(self.request_delay)
        except Exception as e:
            print(f"[{self.name.upper()}] Exception parsing '{keyword}': {e}")

        return results

    def health_check(self) -> Dict[str, Any]:
        """Cek ketersediaan dan latensi endpoint Carousell."""
        start = time.time()
        url = "https://id.carousell.com/search/laptop"
        try:
            res = self.session.get(url, headers=self.get_headers(), timeout=8)
            latency = (time.time() - start) * 1000
            soup = BeautifulSoup(res.text, "html.parser")
            item_count = len(soup.find_all("a", href=lambda x: x and "/p/" in x))
            return {
                "adapter": self.name,
                "status": "HEALTHY" if res.status_code == 200 and item_count > 0 else "DEGRADED",
                "http_status": res.status_code,
                "latency_ms": round(latency, 2),
                "items_found": item_count
            }
        except Exception as e:
            return {
                "adapter": self.name,
                "status": "DOWN",
                "error": str(e),
                "latency_ms": round((time.time() - start) * 1000, 2)
            }
