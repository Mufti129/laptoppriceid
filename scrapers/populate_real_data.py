import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
from models.database import SessionLocal, init_db
from models.catalog import ScrapedListing, MarketPriceStats, MasterVariant, MasterModel, MasterBrand
from pipeline.normalizer import LaptopListingNormalizer
from pipeline.scam_detector import LaptopScamDetector
from pipeline.entity_matcher import LaptopEntityMatcher
from analytics.pricing_engine import LaptopPricingEngine
from scrapers.real_marketplace_scraper import RealMarketplaceScraper, TARGET_KEYWORDS

def purge_synthetic_data(db):
    """Mengosongkan tabel listing sintetis dan statistik harga lama."""
    print("[MIGRATION] Menghapus data listing lama / sintetik dari database...")
    count_deleted = db.query(ScrapedListing).delete()
    db.query(MarketPriceStats).delete()
    db.commit()
    print(f"[MIGRATION] Berhasil menghapus {count_deleted} listing lama.")

def map_carousell_condition(raw_cond: str) -> str:
    """Memetakan kondisi fisik Carousell ke standar Grade fisik sistem."""
    cond_lower = raw_cond.lower()
    if "seperti baru" in cond_lower or "like new" in cond_lower or "brand new" in cond_lower or "baru" in cond_lower:
        return "Grade A+ (Like New 99%)"
    elif "ringan" in cond_lower or "lightly used" in cond_lower or "mulus" in cond_lower:
        return "Grade A (Mulus 95%)"
    elif "digunakan dengan baik" in cond_lower:
        return "Grade A (Mulus 95%)"
    elif "well used" in cond_lower or "baret" in cond_lower or "minus" in cond_lower:
        return "Grade B (Lecet Wajar)"
    return "Grade A (Mulus 95%)"

import json
import re

def clean_price_string(price_val) -> float:
    if price_val is None:
        return 0.0
    if isinstance(price_val, (int, float)):
        return float(price_val)
    s = str(price_val).strip().lower().replace("rp", "").replace("idr", "").strip()
    m_short = re.match(r"^(\d{1,2})[\.,](\d{1,2})$", s)
    if m_short:
        val = float(f"{m_short.group(1)}.{m_short.group(2)}")
        return val * 1_000_000
    digits = re.sub(r"[^\d]", "", s)
    if digits:
        try:
            return float(digits)
        except ValueError:
            return 0.0
    return 0.0

def ingest_real_listings(raw_listings):
    """
    Memproses dan menyimpan listing riil hasil scraping ke database
    melalui Normalizer NLP, Scam Detector, dan Entity Matcher.
    """
    db = SessionLocal()
    init_db()
    
    # 1. Kosongkan data sintetis lama
    purge_synthetic_data(db)
    
    matcher = LaptopEntityMatcher(db)
    saved_count = 0
    scam_count = 0
    matched_count = 0
    
    print(f"\n[INGESTION] Memulai pemrosesan {len(raw_listings)} listing riil...")
    
    for idx, raw in enumerate(raw_listings):
        try:
            # Pastikan field price terisi
            if "price" not in raw or not raw["price"]:
                raw["price"] = raw.get("price_raw", "0")

            # 1. Normalisasi NLP
            norm = LaptopListingNormalizer.normalize_listing(raw)
            
            # Jika harga normalizer 0 tapi raw price ada nilainya, pakai clean_price_string
            if not norm.get("price") or norm["price"] <= 0:
                norm["price"] = clean_price_string(raw.get("price") or raw.get("price_raw"))

            # Jika deskripsi memuat kondisi fisik dari marketplace, petakan
            carousell_grade = map_carousell_condition(raw.get("condition", ""))
            physical_grade = norm["physical_grade"] if norm["physical_grade"] != "Grade A (Mulus 95%)" else carousell_grade
            
            # 2. Entity Matching ke Katalog Master
            var_id, conf, matched_name, msrp = matcher.match(
                norm["title"], norm.get("ram_gb"), norm.get("storage_gb")
            )
            if var_id:
                matched_count += 1
                
            # 3. Scam & DP Detector
            is_scam, scam_type, scam_reason = LaptopScamDetector.evaluate_listing(
                norm["price"], norm["title"], norm["raw_description"], expected_msrp=msrp
            )
            if is_scam:
                scam_count += 1
                
            # 4. Simpan Record Riil ke Database
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
                battery_health_pct=norm.get("battery_health_pct"),
                battery_cycle_count=norm.get("battery_cycle_count"),
                completeness=norm["completeness"],
                physical_grade=physical_grade,
                hinge_condition=norm["hinge_condition"],
                screen_condition=norm["screen_condition"],
                keyboard_condition=norm["keyboard_condition"],
                bios_mdm_status=norm["bios_mdm_status"],
                province="DKI Jakarta" if "Jakarta" in raw.get("city", "") else "Jawa Barat" if "Bandung" in raw.get("city", "") else "Jawa Timur",
                city=raw.get("city", "Jakarta Selatan"),
                seller_name=raw.get("seller_name", "Seller Terverifikasi"),
                seller_type="Individual",
                scraped_at=datetime.utcnow()
            )
            db.add(listing)
            saved_count += 1
            
            if (idx + 1) % 100 == 0:
                db.commit()
                print(f" -> {idx + 1}/{len(raw_listings)} listing riil berhasil diproses...")
                
        except Exception as e:
            print(f"[ERROR] Gagal memproses listing {raw.get('external_id')}: {e}")
            
    db.commit()
    print(f"\n[INGESTION] Berhasil menyimpan {saved_count} listing riil!")
    print(f" - Matched ke Master Catalog: {matched_count} ({matched_count/max(saved_count, 1)*100:.1f}%)")
    print(f" - Listing Tunai Valid: {saved_count - scam_count}")
    print(f" - Terfilter Scam / DP: {scam_count}")
    
    # 5. Rekalkulasi Statistik Pasar FMV
    print("\n[ANALYTICS] Menjalankan kalkulasi ulang statistik pasar (Tukey IQR & FMV)...")
    pricing_engine = LaptopPricingEngine(db)
    recalc_count = pricing_engine.recalculate_all_market_stats()
    print(f"[ANALYTICS] Selesai! {recalc_count} statistik harga varian diperbarui.")
    
    db.close()
    return saved_count

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "real_listings_cache.json")

def main():
    print("=" * 70)
    print("MIGRASI DATASET LAPTOPPRICE ID: 100% REAL LIVE SCRAPED DATA")
    print("=" * 70)
    
    raw_listings = []
    # Cek apakah ada file cache listing riil
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                raw_listings = json.load(f)
            print(f"[CACHE] Memuat {len(raw_listings)} listing riil dari cache {CACHE_FILE}")
        except Exception:
            raw_listings = []

    if not raw_listings:
        scraper = RealMarketplaceScraper(request_delay=0.8)
        raw_listings = scraper.harvest_all_keywords(max_items=1500)
        if raw_listings:
            try:
                os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(raw_listings, f, ensure_ascii=False, indent=2)
                print(f"[CACHE] Berhasil menyimpan cache {len(raw_listings)} listing riil.")
            except Exception as e:
                print(f"[CACHE NOTICE] Gagal menyimpan cache: {e}")
    
    if not raw_listings:
        print("[ERROR] Tidak ada listing yang berhasil di-scrape. Periksa koneksi jaringan.")
        return
        
    ingest_real_listings(raw_listings)
    print("=" * 70)
    print("MIGRASI SELESAI DENGAN SUKSES!")
    print("=" * 70)

if __name__ == "__main__":
    main()
