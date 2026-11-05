# -*- coding: utf-8 -*-
"""
DAG Apache Airflow: Otomasi Scraping Pasar Laptop, Ingesti Spesifikasi LaptopMedia,
dan Kalkulasi Fair Market Value (FMV) OLX.
================================================================================
Schedule: Harian jam 02:00 UTC (09:00 WIB)
SLA: 45 Menit
Owner: laptoppriceid
"""

import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Tambahkan path root proyek
ROOT_DIR = os.getenv("LAPTOPPRICEID_HOME", "/opt/airflow/dags/laptoppriceid")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

default_args = {
    "owner": "laptoppriceid",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60),
}


def task_check_db_connectivity(**context):
    """Memverifikasi integritas dan koneksi database master katalog."""
    import sqlite3
    db_path = os.path.join(ROOT_DIR, "laptop_bekas.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database master {db_path} tidak ditemukan!")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM master_models")
    cnt = cur.fetchone()[0]
    conn.close()
    print(f"[HEALTH] Database OK! Terdata {cnt:,} master model.")
    return cnt


def task_run_olx_laptop_scraping(**context):
    """Menjalankan penarikan data harga iklan laptop terbaru dari OLX."""
    from scrapers.real_marketplace_scraper import RealMarketplaceScraper
    scraper = RealMarketplaceScraper(request_delay=0.5)
    sample_keywords = [
        "thinkpad t480", "thinkpad t14", "thinkpad x1 carbon",
        "macbook air m1", "macbook pro m1", "macbook air m2",
        "asus rog zephyrus", "asus tuf gaming", "acer nitro 5",
        "lenovo legion 5", "hp victus 15", "dell latitude"
    ]
    total_new = 0
    for kw in sample_keywords:
        try:
            items = scraper.scrape_carousell_keyword(kw, max_items=25)
            total_new += len(items)
        except Exception as e:
            print(f"[WARN] Error scraping {kw}: {e}")
    print(f"[OLX/SCRAPER] Berhasil mengambil {total_new} data listing baru.")
    return total_new


def task_run_entity_matching(**context):
    """Mencocokkan listing mentah pasar sekunder ke master_variants."""
    from models.database import SessionLocal
    from models.catalog import ScrapedListing
    from pipeline.entity_matcher import LaptopEntityMatcher

    db = SessionLocal()
    matcher = LaptopEntityMatcher(db)
    unmatched = db.query(ScrapedListing).filter(ScrapedListing.matched_variant_id.is_(None)).all()
    matched_count = 0
    for item in unmatched:
        res = matcher.match_listing(item.title, item.raw_description or "")
        if res.get("variant_id"):
            item.matched_variant_id = res["variant_id"]
            matched_count += 1
    db.commit()
    db.close()
    print(f"[ENTITY MATCHING] Berhasil mencocokkan {matched_count} dari {len(unmatched)} listing.")
    return matched_count


def task_calculate_fair_market_value(**context):
    """Menghitung Fair Market Value (FMV) varian dengan filter Tukey IQR."""
    from models.database import SessionLocal
    from analytics.pricing_engine import LaptopPricingEngine

    db = SessionLocal()
    engine = LaptopPricingEngine(db)
    updated_stats = engine.sync_market_price_stats_table()
    db.close()
    print(f"[FMV ENGINE] Berhasil memperbarui {updated_stats} statistik FMV pasar.")
    return updated_stats


def task_sync_laptopmedia_and_fmv_columns(**context):
    """Menjalankan pipeline sinkronisasi katalog LaptopMedia dan update kolom fair_market_value."""
    import subprocess
    script_path = os.path.join(ROOT_DIR, "pipeline", "sync_master_catalog_with_olx_fmv.py")
    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Gagal menjalankan sync_master_catalog: {res.stderr}")
    print(res.stdout)
    return True


with DAG(
    dag_id="dag_laptop_market_sync",
    default_args=default_args,
    description="Pipeline ETL Master Katalog Laptop, Scraping Pasar & Fair Market Value OLX",
    schedule_interval="0 2 * * *",  # Jam 09:00 WIB
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["laptop", "scraping", "olx", "fmv", "laptopmedia", "production"],
) as dag:

    t1_check_env = PythonOperator(
        task_id="t1_check_database_environment",
        python_callable=task_check_db_connectivity,
    )

    t2_scrape_marketplace = PythonOperator(
        task_id="t2_scrape_marketplace_listings",
        python_callable=task_run_olx_laptop_scraping,
    )

    t3_entity_matching = PythonOperator(
        task_id="t3_match_listings_to_master_variants",
        python_callable=task_run_entity_matching,
    )

    t4_calculate_fmv = PythonOperator(
        task_id="t4_compute_fair_market_values",
        python_callable=task_calculate_fair_market_value,
    )

    t5_sync_master_catalog = PythonOperator(
        task_id="t5_sync_laptopmedia_catalog_and_olx_fmv",
        python_callable=task_sync_laptopmedia_and_fmv_columns,
    )

    t6_data_quality_audit = BashOperator(
        task_id="t6_data_quality_audit",
        bash_command=f"python3 {os.path.join(ROOT_DIR, 'tests', 'test_chassis_taxonomy.py')}",
    )

    # Definisi dependensi alur kerja DAG
    t1_check_env >> t2_scrape_marketplace >> t3_entity_matching >> t4_calculate_fmv >> t5_sync_master_catalog >> t6_data_quality_audit
