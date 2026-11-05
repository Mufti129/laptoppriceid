# -*- coding: utf-8 -*-
"""
DAG: Price Intelligence & Master Catalog Laptop Bekas.
Jadwal: Otomatis setiap hari pukul 03:00 WIB (20:00 UTC).
Sumber Data: Tokopedia, OLX Indonesia, dan Spesifikasi LaptopMedia.
Database Target: laptop_bekas.db
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

LAPTOP_DIR = "/Users/macbookair/Documents/Scrape Data Laptop"
PYTHON_SCRAPE = "/Users/macbookair/Documents/Scrape Data HP/venv/bin/python"
PYTHON_SISTEM = "/Users/macbookair/Documents/sistem/venv/bin/python"

default_args = {
    'owner': 'laptop_intelligence_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def verify_laptop_stats():
    """Verifikasi integritas data terkini pada laptop_bekas.db."""
    db_path = os.path.join(LAPTOP_DIR, "laptop_bekas.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database {db_path} tidak ditemukan!")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM master_brands")
    brands = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM master_models")
    models = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM master_variants")
    variants = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM kode_model_lookup")
    chassis = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM master_models WHERE fair_market_value IS NOT NULL AND fair_market_value > 0")
    fmv_filled = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scraped_listings")
    listings = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM market_price_stats")
    stats = cur.fetchone()[0]
    conn.close()

    print("\n" + "=" * 65)
    print("[AIRFLOW AUDIT] MASTER DATABASE LAPTOP BEKAS TERVERIFIKASI")
    print(f"   - Total Master Brand      : {brands:,} brand")
    print(f"   - Total Master Model      : {models:,} model")
    print(f"   - Total Master Varian     : {variants:,} varian")
    print(f"   - Total Kode Sasis Lookup : {chassis:,} sasis")
    print(f"   - Model dgn FMV Valid     : {fmv_filled:,} ({fmv_filled/max(1,models)*100:.1f}%)")
    print(f"   - Total Listing Pasar     : {listings:,} listing")
    print(f"   - Total Record FMV Stats  : {stats:,} baris statistik")
    print("=" * 65 + "\n")

    if models < 1000 or fmv_filled < 1000:
        raise ValueError(f"Data quality check gagal! Terdata {models} model dan {fmv_filled} FMV valid.")


with DAG(
    dag_id='dag_price_intelligence_laptop',
    default_args=default_args,
    description='Pipeline Terpadu Ingesti Tokopedia, Spesifikasi LaptopMedia & Kalkulasi Fair Market Value OLX',
    schedule='0 3 * * *',  # Pukul 03:00 WIB
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['laptop', 'tokopedia', 'olx', 'laptopmedia', 'price_intelligence', 'master_db'],
) as dag:

    # Task 1: Ingest Tokopedia, Entity Matching Generasional, dan Perhitungan FMV Stats Awal
    task_scrape_tokopedia_laptop = BashOperator(
        task_id='scrape_tokopedia_and_update_laptop_fmv',
        bash_command=(
            f'"{PYTHON_SISTEM}" '
            f'"/Users/macbookair/.gemini/antigravity/scratch/airflow_workspace/scripts/pipeline_laptop_tokopedia.py"'
        ),
    )

    # Task 2: Sinkronisasi Katalog Lengkap LaptopMedia & Perhitungan Kolom Fair Market Value OLX 100%
    task_sync_master_and_olx = BashOperator(
        task_id='sync_laptopmedia_and_olx_fmv',
        bash_command=(
            f'"{PYTHON_SCRAPE}" '
            f'"{os.path.join(LAPTOP_DIR, "pipeline", "sync_master_catalog_with_olx_fmv.py")}"'
        ),
    )

    # Task 3: Verifikasi Agregat Metrik Database
    task_verify_laptop = PythonOperator(
        task_id='verify_laptop_master_stats',
        python_callable=verify_laptop_stats,
    )

    # Task 4: Audit Kualitas Data dan Taksonomi Sasis
    task_audit_taxonomy = BashOperator(
        task_id='audit_chassis_taxonomy_and_integrity',
        bash_command=(
            f'"{PYTHON_SCRAPE}" '
            f'"{os.path.join(LAPTOP_DIR, "tests", "test_chassis_taxonomy.py")}"'
        ),
    )

    task_scrape_tokopedia_laptop >> task_sync_master_and_olx >> task_verify_laptop >> task_audit_taxonomy
