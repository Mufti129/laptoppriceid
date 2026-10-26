"""
Skrip Migrasi & Sinkronisasi Generasi Model / Seri Laptop dan Pembersihan Nama Model Kanonikal.
Memperbarui 1.000 master model di SQLite database (laptop_bekas.db):
1. Menambahkan kolom generation pada master_models jika belum ada.
2. Membersihkan redundansi tahun (YYYY) pada kolom name dan variant_name.
3. Mengisi kolom generation dengan data generasi resmi manufaktur (100% lengkap).
"""

import sqlite3
import os
import sys

# Tambahkan direktori root proyek ke path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from data.generation_taxonomy import resolve_generation_and_canonical_name

def sync_generation_data():
    db_path = os.path.join(PROJECT_DIR, "laptop_bekas.db")
    print(f"[MIGRATION] Menghubungkan ke database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Pastikan kolom generation ada di master_models
    cursor.execute("PRAGMA table_info(master_models);")
    columns = [col[1] for col in cursor.fetchall()]
    if "generation" not in columns:
        print("[MIGRATION] Menambahkan kolom generation ke tabel master_models...")
        cursor.execute("ALTER TABLE master_models ADD COLUMN generation VARCHAR(50);")
    else:
        print("[MIGRATION] Kolom generation sudah tersedia di master_models.")

    # 2. Ambil seluruh model beserta brand-nya
    cursor.execute("""
        SELECT m.id, b.name, m.series, m.name, m.release_year, m.processor_model, m.gpu_model, m.chassis_code
        FROM master_models m
        JOIN master_brands b ON m.brand_id = b.id
        ORDER BY m.id ASC;
    """)
    models = cursor.fetchall()
    print(f"[SYNC] Menemukan {len(models)} model untuk disinkronkan generasi & nama kanonikal...")

    updated_count = 0
    clean_sample = []

    for mid, brand_name, series_name, current_name, release_year, processor_model, gpu_model, chassis_code in models:
        clean_name, generation = resolve_generation_and_canonical_name(
            brand_name=brand_name,
            series_name=series_name,
            current_name=current_name,
            release_year=release_year,
            processor_model=processor_model,
            gpu_model=gpu_model,
            chassis_code=chassis_code
        )

        cursor.execute("""
            UPDATE master_models
            SET name = ?, generation = ?
            WHERE id = ?;
        """, (clean_name, generation, mid))

        # Update variant_name di master_variants
        cursor.execute("""
            SELECT id, ram_gb, storage_gb FROM master_variants WHERE model_id = ?;
        """, (mid,))
        variants = cursor.fetchall()
        for vid, ram, rom in variants:
            new_vname = f"{clean_name} {ram or 8}GB/{rom or 256}GB"
            cursor.execute("""
                UPDATE master_variants
                SET variant_name = ?
                WHERE id = ?;
            """, (new_vname, vid))

        updated_count += 1
        if updated_count <= 10 or updated_count % 100 == 0:
            clean_sample.append((brand_name, current_name, clean_name, generation, release_year))

    conn.commit()
    conn.close()

    print(f"\n[SUCCESS] Berhasil menyinkronkan {updated_count} model dan variannya!")
    print("\n=== SAMPEL HASIL SINKRONISASI & PEMBERSIHAN NAMA ===")
    for b, old, new, gen, yr in clean_sample[:10]:
        print(f"[{b}] \"{old}\" -> \"{new}\" | Generasi: {gen} ({yr})")

if __name__ == "__main__":
    sync_generation_data()
