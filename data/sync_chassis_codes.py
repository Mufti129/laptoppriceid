"""
Skrip Migrasi & Sinkronisasi Kode Sasis / SKU Pabrikan (10 Brand) ke Database SQLite.
"""

import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.chassis_taxonomy import resolve_chassis_code

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "laptop_bekas.db")

def run_chassis_code_sync():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Pastikan kolom chassis_code ada di master_models
    cursor.execute("PRAGMA table_info(master_models);")
    columns = [col[1] for col in cursor.fetchall()]

    if "chassis_code" not in columns:
        print("[MIGRATION] Menambahkan kolom chassis_code ke tabel master_models...")
        cursor.execute("ALTER TABLE master_models ADD COLUMN chassis_code VARCHAR(50);")
        conn.commit()
    else:
        print("[MIGRATION] Kolom chassis_code sudah tersedia di master_models.")

    # 2. Ambil seluruh model beserta nama brand-nya
    cursor.execute("""
        SELECT m.id, b.name, m.series, m.name, m.release_year, m.processor_model, m.gpu_model
        FROM master_models m
        JOIN master_brands b ON m.brand_id = b.id
    """)
    records = cursor.fetchall()
    print(f"[SYNC] Menemukan {len(records)} model laptop untuk disinkronkan kode sasisnya...")

    updated_count = 0
    brand_samples = {}

    for row in records:
        m_id, b_name, s_name, m_name, year, cpu, gpu = row
        chassis = resolve_chassis_code(
            brand_name=b_name,
            series_name=s_name,
            model_name=m_name,
            release_year=year,
            processor_model=cpu,
            gpu_model=gpu
        )

        cursor.execute("""
            UPDATE master_models
            SET chassis_code = ?
            WHERE id = ?
        """, (chassis, m_id))
        updated_count += 1

        if b_name not in brand_samples:
            brand_samples[b_name] = (m_name, chassis)

    conn.commit()
    conn.close()

    print(f"[SYNC] Sukses! {updated_count} model laptop telah disinkronkan dengan kode sasis resmi.")
    print("\n=== CONTOH HASIL SINKRONISASI KODE SASIS PER BRAND ===")
    for b, (m, c) in sorted(brand_samples.items()):
        print(f" - {b:10} | Model: {m:35} -> Kode Sasis: {c}")

if __name__ == "__main__":
    run_chassis_code_sync()
