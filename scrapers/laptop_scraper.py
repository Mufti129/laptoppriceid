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
    """

    def __init__(self):
        self.session = requests.Session()

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    def scrape_olx_laptop(self, keyword: str = "thinkpad", page_limit: int = 2) -> List[Dict[str, Any]]:
        """Scraping publik OLX Indonesia untuk kategori laptop komputer."""
        results = []
        base_url = f"https://www.olx.co.id/komputer_c5155?filter=search_terms_eq_{keyword}"
        
        try:
            res = self.session.get(base_url, headers=self.get_headers(), timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                pass
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
                # 1. Normalisasi
                norm = LaptopListingNormalizer.normalize_listing(raw)
                
                # 2. Entity Matching
                var_id, conf, matched_name, msrp = matcher.match(norm["title"], norm.get("ram_gb"), norm.get("storage_gb"))
                
                # 3. Scam / DP Evaluation
                is_scam, scam_type, scam_reason = LaptopScamDetector.evaluate_listing(
                    norm["price"], norm["title"], norm["raw_description"], expected_msrp=msrp
                )

                # 4. Insert or Update DB
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
                        battery_health_pct=norm["battery_health_pct"],
                        battery_cycle_count=norm["battery_cycle_count"],
                        completeness=norm["completeness"],
                        physical_grade=norm["physical_grade"],
                        hinge_condition=norm["hinge_condition"],
                        screen_condition=norm["screen_condition"],
                        keyboard_condition=norm["keyboard_condition"],
                        bios_mdm_status=norm["bios_mdm_status"],
                        province=norm["province"],
                        city=norm["city"],
                        seller_name=norm["seller_name"],
                        seller_type=norm["seller_type"]
                    )
                    db.add(listing)
                    saved_count += 1
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Gagal menyimpan listing: {e}")
        finally:
            db.close()

        return saved_count
