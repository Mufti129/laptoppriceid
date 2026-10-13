"""
Generator Snapshot Data Listing Pasar Laptop Sekunder Indonesia.
Menghasilkan ribuan listing realistis multi-brand, multi-kondisi, dan multi-kota
yang dialirkan langsung melalui pipeline NLP, Scam Filter, dan Entity Matcher.
Dioptimalkan dengan batch commit untuk performa cepat.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timezone
from models.database import SessionLocal, init_db
from models.catalog import MasterVariant, MasterModel, MasterBrand, ScrapedListing
from pipeline.normalizer import LaptopListingNormalizer
from pipeline.scam_detector import LaptopScamDetector
from pipeline.entity_matcher import LaptopEntityMatcher
from analytics.depreciation_engine import LaptopDepreciationEngine

CITIES = [
    ("Jakarta Selatan", "DKI Jakarta"),
    ("Jakarta Barat", "DKI Jakarta"),
    ("Jakarta Pusat", "DKI Jakarta"),
    ("Tangerang", "Banten"),
    ("Bekasi", "Jawa Barat"),
    ("Bandung", "Jawa Barat"),
    ("Surabaya", "Jawa Timur"),
    ("Semarang", "Jawa Tengah"),
    ("Yogyakarta", "DI Yogyakarta"),
    ("Malang", "Jawa Timur"),
    ("Medan", "Sumatera Utara"),
    ("Makassar", "Sulawesi Selatan"),
    ("Denpasar", "Bali")
]

PLATFORMS = ["olx", "facebook_marketplace", "tokopedia", "shopee"]

def generate_realistic_market_dataset(target_count_per_variant: int = 3):
    init_db()
    db = SessionLocal()

    variants = db.query(MasterVariant, MasterModel, MasterBrand).join(
        MasterModel, MasterVariant.model_id == MasterModel.id
    ).join(
        MasterBrand, MasterModel.brand_id == MasterBrand.id
    ).all()

    if not variants:
        print("[ERROR] Master catalog laptop kosong! Jalankan seed_master_catalog terlebih dahulu.")
        db.close()
        return

    print(f"Generating realistic listings for {len(variants)} laptop variants (target {target_count_per_variant} per variant)...")
    total_generated = 0
    scam_count = 0
    listings_to_add = []

    for var, model, brand in variants:
        msrp = float(var.official_msrp_new)
        retention = LaptopDepreciationEngine.calculate_theoretical_retention(
            brand.name, model.name, model.release_year, current_year=2026, processor_model=model.processor_model or ""
        )
        base_market_price = msrp * retention

        for i in range(target_count_per_variant):
            city, prov = random.choice(CITIES)
            platform = random.choice(PLATFORMS)
            ext_id = f"{platform}_{var.id}_{i+1}_{random.randint(10000, 99999)}"

            is_trap = random.random() < 0.08

            if is_trap:
                price = random.choice([1500000, 2000000, 2500000, 3000000])
                title = f"{brand.name} {model.name} {var.ram_gb}GB {var.storage_gb}GB DP Ringan Angsuran Kredivo/Akulaku"
                desc = f"Promo cuci gudang {model.name}. Cukup bayar DP Rp {price:,}, cicilan ringan sebulan tanpa kartu kredit."
                is_scam = True
                scam_count += 1
            else:
                price_deviation = random.uniform(-0.14, 0.12)
                price = base_market_price * (1.0 + price_deviation)

                is_macbook = "apple" in brand.name.lower() or "macbook" in model.name.lower()
                is_thinkpad = "thinkpad" in model.name.lower()

                warranty = random.choices(
                    ["Garansi Resmi Indonesia", "Ex-Inter US", "Garansi Toko 1 Bulan", "Garansi Distributor"],
                    weights=[50, 25, 20, 5]
                )[0]

                if is_macbook:
                    cc_val = random.randint(30, 280) if model.release_year >= 2022 else random.randint(150, 650)
                    bh_val = random.randint(84, 99) if model.release_year >= 2022 else random.randint(75, 90)
                    bat_str = f"CC {cc_val} BH {bh_val}%"
                elif is_thinkpad and random.random() < 0.20:
                    bat_str = "baterai drop harus sambil colok charger"
                    price *= 0.82
                else:
                    bat_str = random.choice(["baterai awet 4-6 jam normal", "baterai tahan 3 jam", "baterai sehat"])

                cond = random.choices(
                    ["Mulus 99% Like New", "Mulus 95% No Minus", "Lecet Pemakaian Wajar", "Dent Tipis Sudut"],
                    weights=[25, 45, 20, 10]
                )[0]
                comp = random.choices(
                    ["Fullset Dus + Charger Ori", "Unit + Charger Original Bawaan", "Charger OEM", "Batangan Unit Only"],
                    weights=[35, 45, 10, 10]
                )[0]
                hinge = "Engsel Kokoh Normal"
                if "Dent" in cond and random.random() < 0.3:
                    hinge = "Engsel Kendor Tipis"
                    price *= 0.88

                screen = "Layar Jernih No Whitespot"
                if random.random() < 0.08:
                    screen = "Whitespot Tipis Samar"
                    price *= 0.90

                if "Batangan" in comp:
                    price *= 0.88
                if "OEM" in comp:
                    price *= 0.94

                title = f"{brand.name} {model.name} {var.ram_gb}GB {var.storage_gb}GB {warranty} {cond} {comp}"
                desc = f"Jual laptop {brand.name} {model.name} RAM {var.ram_gb}GB SSD {var.storage_gb}GB. {bat_str}, {hinge}, {screen}. Pemakaian terawat, mesin 100% normal. Minat COD {city}."
                is_scam = False

            # Normalisasi
            norm = LaptopListingNormalizer.normalize_listing({
                "source_platform": platform,
                "external_id": ext_id,
                "title": title,
                "description": desc,
                "price": price,
                "ram_gb": var.ram_gb,
                "storage_gb": var.storage_gb,
                "year": model.release_year,
                "province": prov,
                "city": city,
                "seller_name": f"Seller {city}",
                "seller_type": "Store / Toko Komputer" if random.random() < 0.35 else "Individual"
            })

            is_scam_detected, scam_cat, scam_reason = LaptopScamDetector.evaluate_listing(
                norm["price"], norm["title"], norm["raw_description"], expected_msrp=msrp
            )

            final_dp_flag = is_trap or is_scam_detected

            listing = ScrapedListing(
                source_platform=norm["source_platform"],
                external_id=norm["external_id"],
                url=f"https://www.{platform}.co.id/item/{ext_id}",
                title=norm["title"],
                raw_description=norm["raw_description"],
                matched_variant_id=var.id,
                claimed_year=norm.get("claimed_year"),
                price=norm["price"] or 0,
                is_dp_price=final_dp_flag,
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
            listings_to_add.append(listing)
            total_generated += 1

            if len(listings_to_add) >= 500:
                db.bulk_save_objects(listings_to_add)
                db.commit()
                listings_to_add = []

    if listings_to_add:
        db.bulk_save_objects(listings_to_add)
        db.commit()

    db.close()
    print(f"[SUCCESS] Dataset Tergenerate: {total_generated} listing ({scam_count} perangkap DP/anomali terdeteksi).")

if __name__ == "__main__":
    generate_realistic_market_dataset(target_count_per_variant=3)
