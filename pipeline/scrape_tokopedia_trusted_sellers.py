#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Pengambilan Data Harga Laptop di Tokopedia:
FOKUS KHUSUS: SELLER-SELLER TERPERCAYA (Official Store & Power Merchant / Pro).
================================================================================
Tujuan:
1. Menarik data harga aktual dari toko-toko terpercaya (fshop=1,2) di Tokopedia.
2. Memfilter aksesoris, sparepart, dan charger non-unit secara ketat.
3. Memetakan harga pasar ke tipe database internal (713 tipe master).
4. Menghasilkan file ekspor Excel komprehensif:
   - Sheet 1: Data Tarikan Tokopedia (Listing riil seller terpercaya, toko, kota, rating, link).
   - Sheet 2: Ringkasan Harga per Tipe (Harga Min, Median, Rata-rata, Harga Max, Sample).
   - Sheet 3: Pemetaan Database Master (Tipe internal dengan referensi harga pasar Tokopedia).
5. Memperbarui database lokal laptop_bekas.db.
"""

import os
import sys
import re
import time
import json
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Setup Path
ROOT_DIR = Path(__file__).resolve().parent.parent
SISTEM_DIR = Path("/Users/macbookair/Documents/sistem")
DOWNLOADS_DIR = Path("/Users/macbookair/Downloads")

for p in [str(ROOT_DIR), str(SISTEM_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from core.client import AntiBotClient
from models.database import SessionLocal
from models.catalog import ScrapedListing, MarketPriceStats
from pipeline.entity_matcher import LaptopEntityMatcher
from analytics.pricing_engine import LaptopPricingEngine

# Target keyword laptop mencakup kategori internal dengan volume transaksi tertinggi
TARGET_SEARCH_QUERIES = [
    # Asus Mainstream & Budget (Penyumbang Transaksi Tertinggi)
    {"kw": "laptop asus celeron 14 bekas", "target_type": "Intel Celeron 14\"", "brand": "Asus"},
    {"kw": "laptop asus core i3 bekas", "target_type": "Intel Core I3", "brand": "Asus"},
    {"kw": "laptop asus core i5 bekas", "target_type": "Intel Core I5", "brand": "Asus"},
    {"kw": "laptop asus celeron 12 bekas", "target_type": "Intel Celeron 12\"", "brand": "Asus"},
    {"kw": "laptop asus pentium 14 bekas", "target_type": "Pentium 14\"", "brand": "Asus"},
    {"kw": "laptop asus amd e2 bekas", "target_type": "AMD E2", "brand": "Asus"},
    {"kw": "laptop asus amd a4 a9 bekas", "target_type": "AMD A9", "brand": "Asus"},
    {"kw": "laptop asus vivobook 14 bekas", "target_type": "Intel Core I3", "brand": "Asus"},
    {"kw": "laptop asus zenbook bekas", "target_type": "Intel Core I5", "brand": "Asus"},

    # Lenovo Mainstream & Business
    {"kw": "laptop lenovo core i5 bekas", "target_type": "Intel Core I5", "brand": "Lenovo"},
    {"kw": "laptop lenovo core i3 bekas", "target_type": "Intel Core I3", "brand": "Lenovo"},
    {"kw": "laptop lenovo core i7 bekas", "target_type": "Intel Core I7", "brand": "Lenovo"},
    {"kw": "laptop lenovo ryzen 3 bekas", "target_type": "AMD Ryzen 3", "brand": "Lenovo"},
    {"kw": "laptop lenovo ryzen 5 bekas", "target_type": "AMD Ryzen 5", "brand": "Lenovo"},
    {"kw": "laptop lenovo amd a4 a9 bekas", "target_type": "AMD A4", "brand": "Lenovo"},
    {"kw": "laptop thinkpad t480 bekas", "target_type": "Intel Core I5", "brand": "Lenovo"},
    {"kw": "laptop thinkpad x1 carbon bekas", "target_type": "Intel Core I7", "brand": "Lenovo"},
    {"kw": "laptop thinkpad t14 bekas", "target_type": "Intel Core I5", "brand": "Lenovo"},

    # Apple MacBook (Liquiditas Tinggi)
    {"kw": "macbook pro i5 13 bekas", "target_type": "Macbook Pro i5 13\"", "brand": "Apple"},
    {"kw": "macbook air i5 13 bekas", "target_type": "Macbook Air i5 13\"", "brand": "Apple"},
    {"kw": "macbook air i5 11 bekas", "target_type": "Macbook Air i5 11\"", "brand": "Apple"},
    {"kw": "macbook air m1 bekas", "target_type": "Macbook Air M1", "brand": "Apple"},
    {"kw": "macbook pro m1 bekas", "target_type": "Macbook Pro M1", "brand": "Apple"},
    {"kw": "macbook air m2 bekas", "target_type": "Macbook Air M2", "brand": "Apple"},

    # HP / Compaq
    {"kw": "laptop hp ryzen 5 bekas", "target_type": "AMD Ryzen 5", "brand": "HP/Compaq"},
    {"kw": "laptop hp amd athlon bekas", "target_type": "AMD Athlon", "brand": "HP/Compaq"},
    {"kw": "laptop hp elitebook 840 bekas", "target_type": "Intel Core I5", "brand": "HP/Compaq"},
    {"kw": "laptop hp core i3 14 bekas", "target_type": "Intel Core I3", "brand": "HP/Compaq"},

    # Acer
    {"kw": "laptop acer celeron 14 bekas", "target_type": "Intel Celeron 14\"", "brand": "Acer"},
    {"kw": "laptop acer aspire 3 i3 bekas", "target_type": "Intel Core I3", "brand": "Acer"},
    {"kw": "laptop acer swift 3 bekas", "target_type": "Intel Core I5", "brand": "Acer"},

    # Gaming & Workstation Terpopuler di Database Internal
    {"kw": "asus tuf fx506 bekas", "target_type": "Asus Tuf Gaming FX506LH (I5-10300)", "brand": "Gaming"},
    {"kw": "acer nitro 5 an515 bekas", "target_type": "Acer Nitro AN515-52 (I5-8300)", "brand": "Gaming"},
    {"kw": "asus rog strix g531 bekas", "target_type": "Asus ROG Strix G531GD (I7-9750)", "brand": "Gaming"},
    {"kw": "asus tuf fx505 bekas", "target_type": "Asus TUF Gaming FX505GT (I5-9300)", "brand": "Gaming"},
    {"kw": "lenovo ideapad gaming bekas", "target_type": "Lenovo Ideapad Gaming 82K2 AMD Ryzen 5-5600", "brand": "Gaming"},
    {"kw": "hp victus 15 bekas", "target_type": "Hp Pavillion 15\" ec0xxx Amd Ryzen 5-3550", "brand": "Gaming"},

    # Dell & Samsung
    {"kw": "laptop dell latitude 7490 7400 bekas", "target_type": "Intel Core I5", "brand": "Dell"},
    {"kw": "laptop dell xps 13 bekas", "target_type": "Intel Core I7", "brand": "Dell"},
    {"kw": "samsung chromebook celeron bekas", "target_type": "Celeron 12\" Chrome Book", "brand": "Samsung"},
]

def is_accessory_or_scam(title: str, price: int) -> bool:
    """Filter ketat untuk mengeliminasi aksesoris, charger, sparepart, dan scam."""
    # Unit laptop di bawah Rp 800.000 hampir pasti sparepart / charger / mati total
    if price < 800000:
        return True
    
    # Harga di atas batas wajar laptop bekas
    if price > 150000000:
        return True

    t = title.lower()
    
    # Kata kunci sparepart & aksesoris di awal / isi kalimat
    blacklist_words = [
        "charger", "adaptor", "adapter", "kabel", "tas laptop", "sleeve", "casing", "case",
        "baterai", "battery", "motherboard", "mainboard", "mobo", "keyboard", "lcd", "led", "panel",
        "fan", "kipas", "engsel", "hinge", "ram only", "ssd only", "harddisk", "mouse", "skin",
        "stylus", "pen", "stand", "cooler", "cooling pad", "speaker", "fleksibel", "flexible",
        "docking", "hub type c", "converter", "kabel power", "jack dc", "top case", "palmrest"
    ]
    
    if any(t.startswith(w) for w in blacklist_words):
        return True
        
    for w in blacklist_words:
        if re.search(r"\b" + re.escape(w) + r"\b", t):
            # Kecualikan jika judulnya 'bonus tas' atau 'free mouse'
            if not any(b in t for b in [f"free {w}", f"bonus {w}", f"+ {w}", f"plus {w}"]):
                # Periksa apakah ini memang jualan partnya saja
                if any(k in t for k in ["for", "untuk", "utk", "sparepart", "part", "copotan", "kanibal"]):
                    return True

    # Deteksi scam DP / cicilan palsu
    if any(w in t for w in ["dp ", "kredit saja", "bukan harga asli", "khusus cod"]):
        return True

    return False


def fetch_tokopedia_trusted_sellers(client: AntiBotClient, query_str: str, limit: int = 15):
    """Menarik produk Tokopedia khusus seller terpercaya (fshop=1,2: Official Store & Power Merchant)."""
    encoded_kw = query_str.replace(" ", "%20")
    # Parameter fshop=1,2 mengunci pencarian hanya pada toko terverifikasi Tokopedia
    # pmin=800000 mengunci filter harga minimum langsung di server Tokopedia
    params_str = (
        f"device=desktop&source=search&st=product&q={encoded_kw}&"
        f"fshop=1,2&pmin=800000&ob=23&rows={limit}&safe_search=false&scheme=https&start=0"
    )

    gql_query = """query SearchProductQueryV4($params: String!) {
  ace_search_product_v4(params: $params) {
    header {
      totalData
      responseCode
      errorMessage
      __typename
    }
    data {
      products {
        id
        name
        url
        price
        shop {
          id
          name
          city
          __typename
        }
        __typename
      }
      __typename
    }
  }
}"""

    payload = [{
        "operationName": "SearchProductQueryV4",
        "variables": {"params": params_str},
        "query": gql_query
    }]

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://www.tokopedia.com",
        "Referer": f"https://www.tokopedia.com/search?q={encoded_kw}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = client.post("https://gql.tokopedia.com/graphql/SearchProductQueryV4", json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list) and "data" in data[0] and data[0].get("data"):
                ace = data[0]["data"].get("ace_search_product_v4", {})
                return ace.get("data", {}).get("products", [])
    except Exception as e:
        print(f"   [API Error] {query_str}: {e}")
    return []


def run_trusted_sellers_pipeline():
    print("=" * 75)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PIPELINE HARGA TOKOPEDIA (SELLER TERPERCAYA)")
    print("=" * 75)
    print("Filter: Official Store & Power Merchant / Pro (fshop=1,2)")
    print(f"Target Kata Kunci: {len(TARGET_SEARCH_QUERIES)} Kategori Prioritas Database Internal")
    print("-" * 75)

    client = AntiBotClient()
    db = SessionLocal()
    matcher = LaptopEntityMatcher(db)

    all_scraped_records = []
    total_raw = 0
    total_valid = 0
    total_filtered_acc = 0

    try:
        for idx, item in enumerate(TARGET_SEARCH_QUERIES, 1):
            kw = item["kw"]
            target_type = item["target_type"]
            brand = item["brand"]

            print(f"[{idx}/{len(TARGET_SEARCH_QUERIES)}] Menarik Tokopedia: '{kw}' (Target: {target_type})...")
            products = fetch_tokopedia_trusted_sellers(client, kw, limit=20)
            time.sleep(0.8) # Jeda sopan anti-bot

            for p in products:
                total_raw += 1
                name = str(p.get("name") or "").strip()
                price_raw = str(p.get("price") or "0")
                price_clean = int(re.sub(r"[^\d]", "", price_raw) or 0)
                shop_info = p.get("shop") or {}
                shop_name = str(shop_info.get("name") or "Toko Terverifikasi")
                shop_city = str(shop_info.get("city") or "Indonesia")
                url = str(p.get("url") or "")
                ext_id = str(p.get("id") or "")

                # Validasi aksesoris / scam
                if is_accessory_or_scam(name, price_clean):
                    total_filtered_acc += 1
                    continue

                total_valid += 1

                # Matching ke master database internal
                matched_var_id, score, canonical_name, _ = matcher.match(name)
                if score < 50.0:
                    matched_var_id = None
                    canonical_name = "-"

                record = {
                    "kata_kunci_input": kw,
                    "target_tipe_internal": target_type,
                    "merk": brand,
                    "nama_produk_tokopedia": name,
                    "harga_idr": price_clean,
                    "nama_toko": shop_name,
                    "lokasi_toko": shop_city,
                    "status_seller": "Official Store / Power Merchant Pro",
                    "matched_master_model": canonical_name,
                    "confidence_score": round(score, 1) if matched_var_id else 0,
                    "url_produk": url,
                    "waktu_tarikan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                all_scraped_records.append(record)

                # Simpan juga ke database lokal laptop_bekas.db
                existing = db.query(ScrapedListing).filter(
                    ScrapedListing.source_platform == "tokopedia",
                    ScrapedListing.external_id == ext_id
                ).first()

                if not existing and ext_id:
                    new_item = ScrapedListing(
                        source_platform="tokopedia",
                        external_id=ext_id,
                        url=url,
                        title=name,
                        raw_description=f"Seller Terpercaya: {shop_name} ({shop_city})",
                        matched_variant_id=matched_var_id,
                        price=price_clean,
                        city=shop_city,
                        posted_at=datetime.utcnow()
                    )
                    db.add(new_item)

            db.commit()

        print("-" * 75)
        print(f"[REKAP] Total Raw: {total_raw} | Valid Laptop: {total_valid} | Aksesoris/Scam Terfilter: {total_filtered_acc}")

        # Update Master Price Stats
        print("-> Memperbarui Master Database Statistik FMV...")
        engine = LaptopPricingEngine(db)
        saved_stats = engine.sync_market_price_stats_table()
        print(f"-> Statistik FMV diperbarui untuk {saved_stats} varian!")

    finally:
        db.close()

    # Buat File Ekspor Excel & CSV untuk Pemetaan User
    df_raw = pd.DataFrame(all_scraped_records)

    # Sheet 2: Agregat Harga per Tipe Internal
    agg_rows = []
    if not df_raw.empty:
        for t_type, group in df_raw.groupby("target_tipe_internal"):
            prices = group["harga_idr"].values
            agg_rows.append({
                "Tipe Internal Target": t_type,
                "Merk": group["merk"].iloc[0],
                "Jumlah Listing Trusted": len(prices),
                "Harga Pasar Terendah (Min)": int(prices.min()),
                "Harga Pasar Median": int(pd.Series(prices).median()),
                "Harga Pasar Rata-Rata": int(prices.mean()),
                "Harga Pasar Tertinggi (Max)": int(prices.max()),
                "Sampel Toko Terpercaya": ", ".join(group["nama_toko"].unique()[:4])
            })
    df_agg = pd.DataFrame(agg_rows).sort_values(by="Jumlah Listing Trusted", ascending=False)

    # Sheet 3: Integrasi dengan Master File Database Pengguna
    internal_ref_path = DOWNLOADS_DIR / "pemetaan tipe laptop data internal dan data tarikan laptopmedia" / "tipe_laptop_unique_audit_lengkap data internal.xlsx"
    df_master_mapped = pd.DataFrame()
    if internal_ref_path.exists():
        df_int = pd.read_excel(internal_ref_path)
        # Merge dengan data harga agregat Tokopedia
        df_master_mapped = df_int.copy()
        
        # Buat dictionary lookup harga
        lookup_min = dict(zip(df_agg["Tipe Internal Target"], df_agg["Harga Pasar Terendah (Min)"]))
        lookup_max = dict(zip(df_agg["Tipe Internal Target"], df_agg["Harga Pasar Tertinggi (Max)"]))
        lookup_med = dict(zip(df_agg["Tipe Internal Target"], df_agg["Harga Pasar Median"]))
        lookup_cnt = dict(zip(df_agg["Tipe Internal Target"], df_agg["Jumlah Listing Trusted"]))

        df_master_mapped["harga_min_tokopedia"] = df_master_mapped["tipe"].map(lookup_min).fillna(0).astype(int)
        df_master_mapped["harga_max_tokopedia"] = df_master_mapped["tipe"].map(lookup_max).fillna(0).astype(int)
        df_master_mapped["harga_median_tokopedia"] = df_master_mapped["tipe"].map(lookup_med).fillna(0).astype(int)
        df_master_mapped["jumlah_sampel_tokopedia"] = df_master_mapped["tipe"].map(lookup_cnt).fillna(0).astype(int)

    # Simpan ke folder exports dan Downloads
    export_dir = ROOT_DIR / "exports"
    export_dir.mkdir(exist_ok=True)
    
    excel_path_local = export_dir / "tarikan_harga_tokopedia_trusted_sellers.xlsx"
    csv_path_local = export_dir / "tarikan_harga_tokopedia_trusted_sellers.csv"
    excel_path_dl = DOWNLOADS_DIR / "tarikan_harga_tokopedia_trusted_sellers.xlsx"

    with pd.ExcelWriter(excel_path_local, engine="openpyxl") as writer:
        df_raw.to_excel(writer, sheet_name="Data Listing Tokopedia", index=False)
        df_agg.to_excel(writer, sheet_name="Ringkasan Harga per Tipe", index=False)
        if not df_master_mapped.empty:
            df_master_mapped.to_excel(writer, sheet_name="Master DB Terisi Harga", index=False)

    df_raw.to_csv(csv_path_local, index=False)

    # Salin juga ke folder Downloads agar user dapat langsung membukanya di desktop
    import shutil
    shutil.copy(excel_path_local, excel_path_dl)

    print("\n" + "=" * 75)
    print("[BERHASIL SELESAI] File tarikan data harga berhasil dibuat:")
    print(f"1. Excel Workspace : {excel_path_local}")
    print(f"2. Excel Downloads : {excel_path_dl}")
    print(f"3. CSV Workspace   : {csv_path_local}")
    print(f"Total Listing Seller Terpercaya Terkumpul: {len(df_raw):,} listing")
    print(f"Total Tipe Terpetakan Harganya           : {len(df_agg):,} tipe")
    print("=" * 75)

if __name__ == "__main__":
    run_trusted_sellers_pipeline()
