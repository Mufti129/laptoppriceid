import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from models.database import SessionLocal
from models.catalog import ScrapedListing
from pipeline.normalizer import LaptopListingNormalizer
from pipeline.scam_detector import LaptopScamDetector
from pipeline.entity_matcher import LaptopEntityMatcher

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

class LaptopLiveScraper:
    """
    Scraper Multi-Marketplace Laptop Indonesia (OLX, Web Catalog, E-Commerce).
    Dilengkapi emulasi browser, rotasi user-agent, dan integrasi pipeline validasi.
    """

    def __init__(self, request_delay: float = 1.5):
        self.session = requests.Session()
        self.request_delay = request_delay

    def get_headers(self) -> Dict[str, str]:
        """Headers HTTP realistis menyerupai peramban modern."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

    def scrape_olx_laptop(self, keyword: str = "thinkpad", page_limit: int = 2) -> List[Dict[str, Any]]:
        """
        Scraping publik listing laptop pada platform marketplace.
        Menghasilkan struktur listing terstandarisasi.
        """
        results = []
        base_url = f"https://www.olx.co.id/komputer_c5155?filter=search_terms_eq_{keyword}"

        for page in range(1, page_limit + 1):
            target_url = f"{base_url}&page={page}" if page > 1 else base_url
            try:
                res = self.session.get(target_url, headers=self.get_headers(), timeout=12)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    # Parser listing cards
                    cards = soup.select('li[data-aut-id="itemBox"]')
                    for idx, card in enumerate(cards):
                        title_el = card.select_one('span[data-aut-id="itemTitle"]') or card.select_one('div[data-aut-id="itemTitle"]')
                        price_el = card.select_one('span[data-aut-id="itemPrice"]')
                        location_el = card.select_one('span[data-aut-id="itemDetails"]')
                        link_el = card.select_one('a')

                        title = title_el.get_text(strip=True) if title_el else ""
                        price = price_el.get_text(strip=True) if price_el else "0"
                        location = location_el.get_text(strip=True) if location_el else "Jakarta"
                        href = link_el.get("href", "") if link_el else ""
                        full_url = f"https://www.olx.co.id{href}" if href.startswith("/") else href

                        if title:
                            results.append({
                                "source_platform": "olx",
                                "external_id": f"olx_{keyword}_{page}_{idx}",
                                "url": full_url or base_url,
                                "title": title,
                                "description": f"{title} lokasi {location}",
                                "price": price,
                                "city": location.split(",")[0].strip() if "," in location else location,
                                "scraped_at": time.time()
                            })
                time.sleep(self.request_delay)
            except Exception as e:
                print(f"[SCRAPER] Notice on live fetch: {e}")

        return results

    def process_and_save_listings(self, raw_listings: List[Dict[str, Any]]) -> int:
        """Menjalankan Pipeline NLP, Scam Detector, Entity Matcher, dan simpan ke Database."""
        db = SessionLocal()
        matcher = LaptopEntityMatcher(db)
        saved_count = 0

        try:
            for raw in raw_listings:
                norm = LaptopListingNormalizer.normalize_listing(raw)

                var_id, conf, matched_name, msrp = matcher.match(
                    norm["title"], norm.get("ram_gb"), norm.get("storage_gb")
                )

                is_scam, scam_type, scam_reason = LaptopScamDetector.evaluate_listing(
                    norm["price"], norm["title"], norm["raw_description"], expected_msrp=msrp
                )

                listing = db.query(ScrapedListing).filter(
                    ScrapedListing.source_platform == norm["source_platform"],
                    ScrapedListing.external_id == norm["external_id"]
                ).first()

                if not listing:
                    listing = ScrapedListing(
                        source_platform=norm["source_platform"],
                        external_id=norm["external_id"],
                        url=norm["url"],
                        title=norm["title"],
                        raw_description=norm["raw_description"],
                        matched_variant_id=var_id,
                        claimed_year=norm.get("claimed_year"),
                        price=norm["price"] or 0,
                        is_dp_price=is_scam,
                        warranty_type=norm["warranty_type"],
                        warranty_status=norm["warranty_status"],
                        battery_condition=norm["battery_condition"],
                        completeness=norm["completeness"],
                        physical_grade=norm["physical_grade"],
                        hinge_condition=norm["hinge_condition"],
                        screen_condition=norm["screen_condition"],
                        keyboard_condition=norm["keyboard_condition"],
                        bios_mdm_status=norm["bios_mdm_status"],
                        city=norm.get("city", "Jakarta"),
                        is_verified_cash=not is_scam
                    )
                    db.add(listing)
                    saved_count += 1
                else:
                    listing.price = norm["price"] or listing.price
                    listing.matched_variant_id = var_id or listing.matched_variant_id
                    listing.is_dp_price = is_scam

            db.commit()
            print(f"[SCRAPER] Selesai memproses: {saved_count} listing baru tersimpan di database.")
        except Exception as e:
            db.rollback()
            print(f"[SCRAPER] Error saat menyimpan listing: {e}")
        finally:
            db.close()

        return saved_count
