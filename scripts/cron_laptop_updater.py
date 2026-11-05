#!/usr/bin/env python3
"""
Cron & Airflow Periodic Runner untuk Pasar Laptop Bekas.
1. Sinkronisasi harga pasar sekunder via Modular Scraper Adapters.
2. Normalisasi & matching ke Master Varian Laptop (CPU, RAM, Storage).
3. Refresh tabel statistik Fair Market Value (market_price_stats).
"""
import os
import sys
import re
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models.database import SessionLocal
from models.catalog import ScrapedListing, MasterVariant
from scrapers.real_marketplace_scraper import RealMarketplaceScraper
from analytics.pricing_engine import LaptopPricingEngine

def run_laptop_sync(sample_keywords=None):
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI CRON UPDATE HARGA LAPTOP BEKAS")
    print("=" * 60)

    db = SessionLocal()
    try:
        scraper = RealMarketplaceScraper(request_delay=0.4)
        
        # Test health adapter
        health = scraper.health_check_all()
        print(f"-> Status Adapter Carousell: {health['carousell']['status']} ({health['carousell']['latency_ms']:.0f} ms)")
        print(f"-> Status Adapter Tokopedia: {health['tokopedia']['status']} ({health['tokopedia']['latency_ms']:.0f} ms)")

        # Target keyword laptop populer
        if not sample_keywords:
            sample_keywords = [
                "macbook air m1", "macbook pro m1", "thinkpad t480", "thinkpad x1 carbon",
                "asus rog zephyrus", "asus tuf gaming", "lenovo legion 5", "hp victus 15"
            ]

        print(f"\n-> Memindai listing baru untuk {len(sample_keywords)} keyword prioritas...")
        new_count = 0
        for kw in sample_keywords:
            try:
                items = scraper.scrape_carousell_keyword(kw)
                # Ingestion check
                for it in items:
                    ext_id = it.get("external_id", it["url"])
                    existing = db.query(ScrapedListing).filter(ScrapedListing.source_platform == "carousell", ScrapedListing.external_id == ext_id).first()
                    if not existing:
                        raw_p = str(it.get("price", "0"))
                        clean_p = float(re.sub(r"[^0-9]", "", raw_p) or 0)
                        new_listing = ScrapedListing(
                            source_platform="carousell",
                            external_id=it.get("external_id", it["url"]),
                            url=it["url"],
                            title=it["title"],
                            raw_description=it.get("raw_description", ""),
                            matched_variant_id=it.get("matched_variant_id"),
                            price=clean_p,
                            city=it.get("city", "Jakarta"),
                            posted_at=datetime.utcnow()
                        )
                        db.add(new_listing)
                        new_count += 1
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"   [Notice] Gagal ambil '{kw}': {e}")

        print(f"[INGESTION] Selesai! Ditambahkan {new_count} listing laptop baru.")

        # Update Master Stats
        print("\n-> Memperbarui Master Database Statistik FMV Laptop...")
        engine = LaptopPricingEngine(db)
        saved_count = engine.sync_market_price_stats_table()
        print(f"[FMV ENGINE] Berhasil memperbarui {saved_count} varian laptop ke tabel market_price_stats!")

    finally:
        db.close()

if __name__ == "__main__":
    run_laptop_sync()
