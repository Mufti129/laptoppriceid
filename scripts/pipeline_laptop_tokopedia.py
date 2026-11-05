#!/usr/bin/env python3
"""
Pipeline Tarik Harga Laptop Bekas (Tokopedia Exclusive).
Sumber data: Tokopedia (Bebas dari Facebook).
Database target: laptop_bekas.db
"""
import os
import sys
import re
import time
import urllib.parse
from datetime import datetime

LAPTOP_DIR = "/Users/macbookair/Documents/Scrape Data Laptop"
SISTEM_DIR = "/Users/macbookair/Documents/sistem"

for d in [LAPTOP_DIR, SISTEM_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from models.database import SessionLocal
from models.catalog import ScrapedListing, MasterVariant, MasterModel, MarketPriceStats
from analytics.pricing_engine import LaptopPricingEngine
from pipeline.entity_matcher import LaptopEntityMatcher
from core.client import AntiBotClient

DEFAULT_LAPTOP_KEYWORDS_BEKAS = [
    "macbook air m1 bekas", "macbook air m2 bekas", "macbook pro m1 bekas", "macbook pro m2 bekas",
    "thinkpad x1 carbon bekas", "thinkpad t480 bekas", "thinkpad t490 bekas", "thinkpad t14 bekas",
    "asus rog zephyrus bekas", "asus tuf gaming bekas", "asus zenbook bekas", "asus vivobook bekas",
    "lenovo legion 5 bekas", "lenovo ideapad gaming bekas", "lenovo loq bekas",
    "acer nitro 5 bekas", "acer swift 3 bekas", "acer predator helios bekas",
    "hp victus 15 bekas", "hp elitebook 840 bekas", "hp envy x360 bekas",
    "dell xps 13 bekas", "dell latitude 7490 bekas", "dell latitude 7400 bekas"
]

DEFAULT_LAPTOP_KEYWORDS_BARU = [
    "macbook air m1 baru segel resmi", "macbook air m2 baru resmi",
    "thinkpad t14 baru garansi resmi", "thinkpad x1 carbon baru",
    "asus rog zephyrus g14 baru", "asus tuf gaming baru resmi",
    "lenovo legion 5 baru resmi", "lenovo loq baru",
    "acer nitro 5 baru", "hp victus 15 baru resmi"
]

def is_accessory(title, price):
    if price < 1200000:
        return True
    t = title.lower()
    starts_with_acc = any(t.startswith(w) for w in [
        "charger", "adaptor", "adapter", "kabel", "tas", "sleeve", "casing", "case",
        "baterai", "battery", "motherboard", "mainboard", "keyboard", "lcd", "led", "panel",
        "fan", "kipas", "engsel", "hinge", "ram only", "ssd only", "harddisk", "mouse", "skin"
    ])
    if starts_with_acc:
        return True
    if re.search(r"\b(for|untuk|utk)\s+(macbook|laptop|asus|lenovo|thinkpad|acer|hp|dell)\b", t):
        return True
    return False

def search_tokopedia_laptop(client, keyword, limit=20, condition="bekas"):
    encoded_kw = urllib.parse.quote(keyword)
    fcond_param = "&fcond=1" if condition.lower() == "baru" else "&fcond=2"
    params_str = (
        f"device=desktop&navsource=&ob=23&page=1&q={encoded_kw}{fcond_param}&"
        f"related=true&rows={limit}&safe_search=false&scheme=https&"
        f"source=search&st=product&start=0"
    )
    
    query = """query SearchProductQueryV4($params: String!) {
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
        "query": query
    }]

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://www.tokopedia.com",
        "Referer": f"https://www.tokopedia.com/search?q={encoded_kw}",
        "Sec-Ch-Ua": '"Chromium";v="120", "Google Chrome";v="120"',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = client.post("https://gql.tokopedia.com/graphql/SearchProductQueryV4", json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list) and 'data' in data[0] and data[0].get('data'):
                return data[0]['data']['ace_search_product_v4']['data']['products']
    except Exception as e:
        print(f"   [Tokopedia API Error] {e}")
    return []

def clean_price(price_str):
    if not price_str:
        return 0
    cleaned = re.sub(r"[^\d]", "", str(price_str))
    return int(cleaned) if cleaned else 0

def run_pipeline(keywords=None, condition="bekas"):
    print("=" * 65)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI PIPELINE LAPTOP (SUMBER: TOKOPEDIA | KONDISI: {condition.upper()})")
    print("=" * 65)

    db = SessionLocal()
    client = AntiBotClient()
    
    if condition.lower() == "baru":
        keywords = keywords or DEFAULT_LAPTOP_KEYWORDS_BARU
    else:
        keywords = keywords or DEFAULT_LAPTOP_KEYWORDS_BEKAS

    total_scraped = 0
    total_inserted = 0
    total_skipped = 0
    matcher = LaptopEntityMatcher(db)

    try:
        for kw in keywords:
            print(f"-> [Tokopedia] Menarik data listing Laptop ({condition.upper()}): '{kw}'...")
            products = search_tokopedia_laptop(client, kw, limit=15, condition=condition)
            time.sleep(1.0) # Jeda sopan anti-bot

            for p in products:
                total_scraped += 1
                title = p.get("name", "").strip()
                price = clean_price(p.get("price", "0"))

                # Filter harga minimal dan kata kunci aksesoris / sparepart
                if is_accessory(title, price):
                    total_skipped += 1
                    continue

                # Match ke Master Model & Varian Laptop via LaptopEntityMatcher
                matched_var_id, score, name, _ = matcher.match(title)
                if score < 50.0:
                    matched_var_id = None

                ext_id = str(p.get("id"))
                existing = db.query(ScrapedListing).filter(
                    ScrapedListing.source_platform == "tokopedia",
                    ScrapedListing.external_id == ext_id
                ).first()

                if not existing:
                    city = p.get("shop", {}).get("city", "Jakarta") if p.get("shop") else "Jakarta"
                    new_item = ScrapedListing(
                        source_platform="tokopedia",
                        external_id=ext_id,
                        url=p.get("url", ""),
                        title=title,
                        raw_description=f"Seller: {p.get('shop', {}).get('name', '')} di {city} | Kondisi: {condition.upper()}",
                        matched_variant_id=matched_var_id,
                        price=price,
                        condition=condition.upper(),
                        city=city,
                        posted_at=datetime.utcnow()
                    )
                    db.add(new_item)
                    total_inserted += 1

            db.commit()

        print(f"\n[INGESTION TOKOPEDIA LAPTOP] Selesai: {total_scraped} discrape, {total_inserted} baru, {total_skipped} skip/aksesoris.")

        # Recalculate Master Price Stats (FMV)
        print("-> Memperbarui Master Database Statistik FMV Laptop...")
        engine = LaptopPricingEngine(db)
        saved_count = engine.sync_market_price_stats_table()
        print(f"[FMV STATS] Berhasil memperbarui {saved_count} varian laptop ke tabel market_price_stats!")

    finally:
        db.close()

    print("=" * 65)
    print(f"[SUCCESS] Pipeline Laptop (Tokopedia | {condition.upper()}) Selesai Sukses!")
    print("=" * 65)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline Scraper Laptop Tokopedia")
    parser.add_argument("--condition", choices=["bekas", "baru", "both"], default="bekas", help="Pilihan kondisi: bekas, baru, atau both")
    parser.add_argument("--dry-run", action="store_true", help="Mode uji coba")
    args = parser.parse_args()

    if args.condition == "both":
        run_pipeline(condition="bekas")
        run_pipeline(condition="baru")
    else:
        run_pipeline(condition=args.condition)
