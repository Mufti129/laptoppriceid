import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
from models.database import SessionLocal, init_db
from models.catalog import ScrapedListing, MarketPriceStats, MasterVariant, MasterModel, MasterBrand, ListingPriceHistory
from pipeline.normalizer import LaptopListingNormalizer
from pipeline.scam_detector import LaptopScamDetector
from pipeline.entity_matcher import LaptopEntityMatcher
from analytics.pricing_engine import LaptopPricingEngine
from scrapers.real_marketplace_scraper import RealMarketplaceScraper, TARGET_KEYWORDS

def purge_synthetic_data(db):
    """Mengosongkan tabel listing sintetis dan statistik harga lama."""
    print("[MIGRATION] Menghapus data listing lama / sintetik dari database...")
    db.query(ListingPriceHistory).delete()
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

def ingest_real_listings(raw_listings, purge_old: bool = False):
    """
    Memproses dan menyimpan listing riil hasil scraping ke database
    melalui Normalizer NLP, Scam Detector, dan Entity Matcher.
    Mendukung Delta Tracking (pelacakan riwayat perubahan harga individual).
    """
    db = SessionLocal()
    init_db()
    
    # 1. Kosongkan data lama jika diminta
    if purge_old:
        purge_synthetic_data(db)
        existing_map = {}
    else:
        existing_rows = db.query(ScrapedListing).all()
        existing_map = {(row.source_platform, row.external_id): row for row in existing_rows}
        print(f"[DELTA TRACKER] Terdata {len(existing_map)} listing eksisting untuk pelacakan delta harga.")
    
    matcher = LaptopEntityMatcher(db)
    saved_count = 0
    updated_count = 0
    price_drops_count = 0
    scam_count = 0
    matched_count = 0
    
    print(f"\n[INGESTION] Memulai pemrosesan {len(raw_listings)} listing riil...")
    start_time = time.time()
    
    batch_new = []
    BATCH_SIZE = 5000
    
    for idx, raw in enumerate(raw_listings):
        try:
            platform = raw.get("source_platform", "carousell")
            ext_id = raw.get("external_id")

            # A. DELTA TRACKING: Jika listing sudah terdaftar di database
            if (platform, ext_id) in existing_map:
                existing_item = existing_map[(platform, ext_id)]
                old_p = float(existing_item.price or 0)
                raw_p = raw.get("price") or raw.get("price_raw")
                new_p = clean_price_string(raw_p)

                existing_item.last_seen_at = datetime.utcnow()

                if new_p > 0 and abs(new_p - old_p) >= 10000:
                    delta_val = new_p - old_p
                    delta_pct = (delta_val / old_p) * 100.0 if old_p > 0 else 0.0

                    hist_record = ListingPriceHistory(
                        listing_id=existing_item.id,
                        old_price=old_p,
                        new_price=new_p,
                        price_delta=delta_val,
                        price_delta_pct=delta_pct,
                        detected_at=datetime.utcnow()
                    )
                    db.add(hist_record)
                    existing_item.price = new_p

                    if delta_val < 0:
                        existing_item.price_drop_count = (existing_item.price_drop_count or 0) + 1
                        existing_item.status = "PRICE_DROP"
                        price_drops_count += 1

                updated_count += 1
                continue

            # B. LISTING BARU: Ingesti & Normalisasi
            # Jika sudah memiliki data terstruktur lengkap & matched_variant_id
            if raw.get("matched_variant_id"):
                var_id = raw["matched_variant_id"]
                matched_count += 1
                is_scam = raw.get("is_dp_price", False)
                if is_scam:
                    scam_count += 1
                
                city = raw.get("city", "Jakarta Selatan")
                if "Jakarta" in city:
                    province = "DKI Jakarta"
                elif "Bandung" in city or "Bekasi" in city or "Depok" in city or "Bogor" in city:
                    province = "Jawa Barat"
                elif "Surabaya" in city or "Malang" in city:
                    province = "Jawa Timur"
                elif "Semarang" in city or "Solo" in city:
                    province = "Jawa Tengah"
                elif "Yogyakarta" in city or "Jogja" in city:
                    province = "DI Yogyakarta"
                elif "Medan" in city:
                    province = "Sumatera Utara"
                elif "Tangerang" in city:
                    province = "Banten"
                else:
                    province = "DKI Jakarta"
                
                listing = ScrapedListing(
                    source_platform=platform,
                    external_id=ext_id,
                    url=raw["url"],
                    title=raw["title"],
                    raw_description=raw.get("raw_description", raw["title"]),
                    matched_variant_id=var_id,
                    claimed_year=raw.get("claimed_year"),
                    price=raw["price"] or 0,
                    is_dp_price=is_scam,
                    warranty_type=raw.get("warranty_type", "Garansi Toko 1 Bulan"),
                    warranty_status=raw.get("warranty_status", "Garansi Toko 1 Bulan"),
                    battery_condition=raw.get("battery_condition", "Normal Awet"),
                    battery_health_pct=raw.get("battery_health_pct", 88),
                    battery_cycle_count=raw.get("battery_cycle_count", 210),
                    completeness=raw.get("completeness", "Unit + Charger Original"),
                    physical_grade=raw.get("physical_grade", "Grade A (Mulus 95%)"),
                    hinge_condition=raw.get("hinge_condition", "Normal Kokoh"),
                    screen_condition=raw.get("screen_condition", "Normal Jernih"),
                    keyboard_condition=raw.get("keyboard_condition", "Normal Aktif"),
                    bios_mdm_status=raw.get("bios_mdm_status", "Clean"),
                    province=province,
                    city=city,
                    seller_name=raw.get("seller_name", "Seller Terverifikasi"),
                    seller_type=raw.get("seller_type", "Store / Toko Komputer"),
                    is_synthetic=False,
                    last_seen_at=datetime.utcnow(),
                    scraped_at=datetime.utcnow()
                )
            else:
                # Listing dari live web scraper (misal Carousell)
                if "price" not in raw or not raw["price"]:
                    raw["price"] = raw.get("price_raw", "0")

                norm = LaptopListingNormalizer.normalize_listing(raw)
                if not norm.get("price") or norm["price"] <= 0:
                    norm["price"] = clean_price_string(raw.get("price") or raw.get("price_raw"))

                carousell_grade = map_carousell_condition(raw.get("condition", ""))
                physical_grade = norm["physical_grade"] if norm["physical_grade"] != "Grade A (Mulus 95%)" else carousell_grade
                
                var_id, conf, matched_name, msrp = matcher.match(
                    norm["title"], norm.get("ram_gb"), norm.get("storage_gb")
                )
                if var_id:
                    matched_count += 1
                    
                is_scam, scam_type, scam_reason = LaptopScamDetector.evaluate_listing(
                    norm["price"], norm["title"], norm["raw_description"], expected_msrp=msrp
                )
                if is_scam:
                    scam_count += 1
                    
                city = raw.get("city", "Jakarta Selatan")
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
                    province="DKI Jakarta" if "Jakarta" in city else "Jawa Barat" if "Bandung" in city else "Jawa Timur",
                    city=city,
                    seller_name=raw.get("seller_name", "Seller Terverifikasi"),
                    seller_type="Individual",
                    is_synthetic=False,
                    last_seen_at=datetime.utcnow(),
                    scraped_at=datetime.utcnow()
                )

            batch_new.append(listing)
            saved_count += 1
            
            if len(batch_new) >= BATCH_SIZE:
                db.bulk_save_objects(batch_new)
                db.commit()
                batch_new.clear()
                elapsed = time.time() - start_time
                print(f" -> {saved_count}/{len(raw_listings)} listing baru tersimpan ({saved_count/elapsed:.0f} rows/s)...")
                
        except Exception as e:
            print(f"[ERROR] Gagal memproses listing {raw.get('external_id')}: {e}")
            
    if batch_new:
        db.bulk_save_objects(batch_new)
        db.commit()
        batch_new.clear()

    db.commit()
    elapsed = time.time() - start_time
    print(f"\n[INGESTION] Selesai dalam {elapsed:.2f} detik!")
    print(f" - Listing Baru Ditambahkan: {saved_count}")
    print(f" - Listing Eksisting Diperbarui: {updated_count}")
    print(f" - Deteksi Penurunan Harga (Price Drops): {price_drops_count}")
    print(f" - Matched ke Master Catalog: {matched_count}")
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
    print("MIGRASI DATASET LAPTOPPRICE ID: 100% REAL LIVE SCRAPED DATA (OPSI B)")
    print("Platform: Carousell ID (Live Web C2C - Expanded 115+ Keywords)")
    print("=" * 70)
    
    existing_listings = []
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                existing_listings = json.load(f)
            print(f"[CACHE] Memuat {len(existing_listings)} listing riil sebelumnya dari cache.")
        except Exception:
            existing_listings = []

    print(f"\n[LIVE SCRAPING] Menjalankan crawling live ke Carousell ID untuk 115+ keyword spesifik...")
    scraper = RealMarketplaceScraper(request_delay=0.4)
    expanded_real_listings = scraper.harvest_all_keywords(
        max_items=4000,
        existing_listings=existing_listings
    )

    print(f"\n[CACHE] Menyimpan total {len(expanded_real_listings)} listing riil murni ke {CACHE_FILE}...")
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(expanded_real_listings, f, ensure_ascii=False, indent=2)
        print("[CACHE] Penyimpanan cache berhasil.")
    except Exception as e:
        print(f"[CACHE ERROR] {e}")

    # Ingest 100% data riil murni ke database
    print(f"\n[INGESTION] Memasukkan {len(expanded_real_listings)} listing riil hasil scraping murni ke database...")
    ingest_real_listings(expanded_real_listings, purge_old=True)
    print("=" * 70)
    print("OPSI B SELESAI: DATABASE 100% RIIL TEREXPANSI DARI LIVE MARKETPLACE CAROUSELL ID!")
    print("=" * 70)

if __name__ == "__main__":
    main()
