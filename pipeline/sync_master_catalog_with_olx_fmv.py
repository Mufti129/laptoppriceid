#!/usr/bin/env python3
"""
Pipeline Sinkronisasi Database Master Katalog Laptop:
1. Migrasi skema: Menambahkan kolom fair_market_value ke master_models & master_variants.
2. Impor tabel kode_model_lookup (20.331 baris) untuk reverse lookup kode sasis/SKU.
3. Sinkronisasi master katalog dari laptopmedia_master.db (14.033 model varian) ke master_models & master_variants.
4. Kalkulasi fair_market_value berbasis data tarikan OLX (olx_scraper.db & integrasi_pasar_laptopmedia.db),
   serta kalibrasi kurva ekonometrik pasar sekunder Indonesia.
"""

import os
import re
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

TARGET_DB_PATH = ROOT_DIR / "laptop_bekas.db"
EXTRACT_DIR = Path("/tmp/integrasi_harga_laptop_extracted/integrasi_harga_laptop/data")
ZIP_SOURCE_PATH = Path("/Users/macbookair/Downloads/integrasi_harga_laptop.zip")

def ensure_source_files_extracted():
    if not (EXTRACT_DIR / "laptopmedia_master.db").exists():
        if ZIP_SOURCE_PATH.exists():
            import zipfile
            print(f"[EXTRACT] Mengekstrak sumber data dari {ZIP_SOURCE_PATH}...")
            with zipfile.ZipFile(ZIP_SOURCE_PATH, 'r') as zf:
                zf.extractall("/tmp/integrasi_harga_laptop_extracted")
            print("[EXTRACT] Selesai ekstraksi!")

ensure_source_files_extracted()

LAPTOPMEDIA_DB_PATH = EXTRACT_DIR / "laptopmedia_master.db"
INTEGRASI_DB_PATH = EXTRACT_DIR / "integrasi_pasar_laptopmedia.db"
OLX_DB_PATH = EXTRACT_DIR / "olx_scraper.db"


def ensure_schema_migrations(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(master_models)")
    model_cols = [c[1] for c in cur.fetchall()]
    if "fair_market_value" not in model_cols:
        print("[MIGRATE] Menambahkan kolom fair_market_value ke master_models...")
        cur.execute("ALTER TABLE master_models ADD COLUMN fair_market_value NUMERIC(15, 2)")

    cur.execute("PRAGMA table_info(master_variants)")
    variant_cols = [c[1] for c in cur.fetchall()]
    if "fair_market_value" not in variant_cols:
        print("[MIGRATE] Menambahkan kolom fair_market_value ke master_variants...")
        cur.execute("ALTER TABLE master_variants ADD COLUMN fair_market_value NUMERIC(15, 2)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS kode_model_lookup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_model TEXT NOT NULL,
        kode_norm TEXT NOT NULL,
        varian_kode TEXT,
        brand TEXT,
        nama_komersial TEXT,
        seri TEXT,
        generasi TEXT,
        tahun_rilis INTEGER,
        ukuran_layar TEXT,
        cpu TEXT,
        gpu TEXT,
        berat TEXT,
        nama_seri_lengkap TEXT,
        url_sumber TEXT
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kml_norm ON kode_model_lookup(kode_norm)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kml_model ON kode_model_lookup(kode_model)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kml_brand ON kode_model_lookup(brand)")
    conn.commit()


def load_olx_fair_values() -> tuple[dict, dict]:
    by_code = {}
    by_model_key = {}

    if INTEGRASI_DB_PATH.exists():
        try:
            conn_int = sqlite3.connect(str(INTEGRASI_DB_PATH))
            cur_int = conn_int.cursor()
            cur_int.execute("""
                SELECT "Kode Model Pabrikan", "Model", "Brand",
                       "Harga Pasar Median (Rp)", "Rata-Rata Harga OLX (Rp)", "Harga Pasar Termurah (Rp)"
                FROM laptop_market_summary
                WHERE "Total Iklan Pasar" > 0
            """)
            for code_raw, model_raw, brand_raw, med_rp, olx_rp, min_rp in cur_int.fetchall():
                price_val = 0
                for cand in (olx_rp, med_rp, min_rp):
                    digits = re.sub(r"[^\d]", "", str(cand or ""))
                    if digits and int(digits) > 500000:
                        price_val = int(digits)
                        break
                if price_val > 0:
                    if code_raw and code_raw != "-":
                        c_norm = re.sub(r"[^a-zA-Z0-9]", "", str(code_raw)).upper()
                        if len(c_norm) >= 3:
                            by_code[c_norm] = price_val
                    b_norm = (brand_raw or "").strip().lower()
                    m_norm = (model_raw or "").strip().lower()
                    m_key = f"{b_norm} {m_norm}"
                    by_model_key[m_key] = price_val

            cur_int.execute("""
                SELECT "Kode Model Pabrikan", "Brand", "Model", "Harga Median (Rp)"
                FROM laptop_variant_prices
                WHERE "Harga Median (Rp)" > 0
            """)
            for code_raw, brand_raw, model_raw, med_p in cur_int.fetchall():
                if med_p and med_p > 500000:
                    if code_raw and code_raw != "-":
                        c_norm = re.sub(r"[^a-zA-Z0-9]", "", str(code_raw)).upper()
                        by_code[c_norm] = int(med_p)
            conn_int.close()
            print(f"[OLX] Berhasil memuat {len(by_code)} referensi harga sasis dan {len(by_model_key)} model dari integrasi OLX.")
        except Exception as e:
            print(f"[WARN] Gagal membaca data pasar integrasi: {e}")

    if OLX_DB_PATH.exists():
        try:
            conn_olx = sqlite3.connect(str(OLX_DB_PATH))
            cur_olx = conn_olx.cursor()
            cur_olx.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='laptop'")
            if cur_olx.fetchone():
                cur_olx.execute("""
                    SELECT merek, model_seri, harga
                    FROM laptop
                    WHERE harga >= 800000 AND harga <= 80000000
                """)
                prices_by_mk = {}
                for b_raw, m_raw, p_raw in cur_olx.fetchall():
                    b_str = (b_raw or "").strip().lower()
                    m_str = (m_raw or "").strip().lower()
                    if b_str and m_str and p_raw:
                        mk = f"{b_str} {m_str}"
                        prices_by_mk.setdefault(mk, []).append(float(p_raw))
                for mk, plist in prices_by_mk.items():
                    plist.sort()
                    med_p = plist[len(plist) // 2]
                    if mk not in by_model_key:
                        by_model_key[mk] = int(med_p)
            conn_olx.close()
        except Exception as e:
            print(f"[WARN] Gagal membaca data mentah OLX: {e}")

    return by_code, by_model_key


def calculate_econometric_fmv(brand: str, model: str, cpu: str, gpu: str, ram_gb: int, storage_gb: int, release_year: int, msrp_idr: float) -> float:
    try:
        yr = int(release_year) if release_year else 2022
    except Exception:
        yr = 2022

    age = max(0, 2026 - yr)
    b_low = (brand or "").lower()
    gpu_low = (gpu or "").lower()
    cpu_low = (cpu or "").lower()

    if not msrp_idr or msrp_idr <= 0:
        is_gaming = any(k in gpu_low for k in ["rtx", "gtx", "radeon rx"]) or any(k in model.lower() for k in ["rog", "tuf", "nitro", "legion", "loq", "victus", "predator", "omen", "katana"])
        is_flagship = any(k in model.lower() for k in ["x1 carbon", "xps", "zenbook", "spectre", "macbook pro"])
        if is_flagship or (b_low == "apple" and "pro" in model.lower()):
            base_msrp = 22999000
        elif is_gaming:
            base_msrp = 15999000
        elif b_low == "apple":
            base_msrp = 14999000
        else:
            base_msrp = 8999000
    else:
        base_msrp = float(msrp_idr)

    if b_low == "apple":
        rate = 0.12
    elif any(k in gpu_low for k in ["rtx", "gtx", "radeon rx"]):
        rate = 0.17
    elif any(k in model.lower() for k in ["thinkpad", "xps", "zenbook", "latitude", "elitebook"]):
        rate = 0.15
    else:
        rate = 0.19

    depreciated = base_msrp * ((1.0 - rate) ** age)

    hw_mult = 1.0
    if ram_gb >= 32:
        hw_mult += 0.08
    elif ram_gb >= 16:
        hw_mult += 0.04
    elif ram_gb <= 4:
        hw_mult -= 0.12

    if storage_gb >= 1000:
        hw_mult += 0.05
    elif storage_gb <= 256:
        hw_mult -= 0.06

    final_fmv = depreciated * hw_mult
    floor_price = 1200000 if age >= 6 else 1800000
    ceiling_price = base_msrp * 0.90
    final_fmv = max(floor_price, min(ceiling_price, final_fmv))
    rounded = int(round(final_fmv / 50000.0)) * 50000
    return float(rounded)


def sync_kode_model_lookup(target_conn: sqlite3.Connection):
    if not LAPTOPMEDIA_DB_PATH.exists():
        print(f"[WARN] Database LaptopMedia tidak ditemukan di {LAPTOPMEDIA_DB_PATH}")
        return 0

    src_conn = sqlite3.connect(str(LAPTOPMEDIA_DB_PATH))
    src_cur = src_conn.cursor()
    src_cur.execute("SELECT count(*) FROM kode_model_lookup")
    src_count = src_cur.fetchone()[0]

    target_cur = target_conn.cursor()
    target_cur.execute("SELECT count(*) FROM kode_model_lookup")
    curr_count = target_cur.fetchone()[0]

    if curr_count >= src_count and curr_count > 0:
        print(f"[CHASSIS] Tabel kode_model_lookup sudah terisi ({curr_count:,} baris). Melewati migrasi ulang.")
        src_conn.close()
        return curr_count

    print(f"[CHASSIS] Mengimpor {src_count:,} baris kode model / sasis dari LaptopMedia...")
    target_cur.execute("DELETE FROM kode_model_lookup")

    src_cur.execute("""
        SELECT kode_model, kode_norm, varian_kode, brand, nama_komersial, seri,
               generasi, tahun_rilis, ukuran_layar, cpu, gpu, berat, nama_seri_lengkap, url_sumber
        FROM kode_model_lookup
    """)
    rows = src_cur.fetchall()
    target_cur.executemany("""
        INSERT INTO kode_model_lookup (
            kode_model, kode_norm, varian_kode, brand, nama_komersial, seri,
            generasi, tahun_rilis, ukuran_layar, cpu, gpu, berat, nama_seri_lengkap, url_sumber
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    target_conn.commit()
    src_conn.close()
    print(f"[CHASSIS] Berhasil mengimpor {len(rows):,} entri reverse lookup kode sasis.")
    return len(rows)


def sync_master_models_and_variants(target_conn: sqlite3.Connection, olx_by_code: dict, olx_by_mk: dict):
    if not LAPTOPMEDIA_DB_PATH.exists():
        print(f"[WARN] Database LaptopMedia tidak ditemukan di {LAPTOPMEDIA_DB_PATH}")
        return

    src_conn = sqlite3.connect(str(LAPTOPMEDIA_DB_PATH))
    src_cur = src_conn.cursor()
    src_cur.execute("SELECT count(*) FROM laptop_series_master")
    total_src = src_cur.fetchone()[0]
    print(f"[SYNC] Membaca {total_src:,} seri laptop dari LaptopMedia master...")

    target_cur = target_conn.cursor()

    target_cur.execute("SELECT id, LOWER(name) FROM master_brands")
    brand_map = {row[1]: row[0] for row in target_cur.fetchall()}

    def get_or_create_brand_id(b_name: str) -> int:
        b_clean = (b_name or "").strip()
        b_key = b_clean.lower()
        if b_key in brand_map:
            return brand_map[b_key]
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        target_cur.execute(
            "INSERT INTO master_brands (name, country_origin, tier_category, is_active, created_at) VALUES (?, ?, ?, ?, ?)",
            (b_clean, "Global", "Mainstream", 1, now_str)
        )
        new_id = target_cur.lastrowid
        brand_map[b_key] = new_id
        return new_id

    target_cur.execute('SELECT id, brand_id, name, chassis_code, release_year FROM master_models')
    existing_models = {}
    for r in target_cur.fetchall():
        b_id, m_name, c_code, yr = r[1], r[2], r[3], r[4]
        c_norm = re.sub(r"[^a-zA-Z0-9]", "", str(c_code or "")).upper()
        existing_models[(b_id, m_name.lower(), c_norm)] = r[0]

    src_cur.execute("""
        SELECT Brand, Model, "Kode Model Pabrikan", Generasi, "Generasi Komersial", "Generasi Silsilah",
               Seri, "Tahun Rilis", "Kategori Laptop", "MSRP Rilis Perdana", "Processor / CPU",
               "Graphics / GPU", "Kapasitas RAM", "Varian Storage", "Slot M.2 / Upgrade", "Tipe Layar",
               "Ukuran Layar", Resolusi, "Refresh Rate", Baterai, "Material Bodi", Berat, "OS Awal",
               "Nama Seri Lengkap", "URL Sumber"
        FROM laptop_series_master
    """)
    src_rows = src_cur.fetchall()

    new_models_count = 0
    updated_models_count = 0
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for r in src_rows:
        brand_str = str(r[0] or "").strip()
        model_str = str(r[1] or "").strip()
        # Bersihkan akhiran tahun redundan seperti (2023) atau (2024)
        model_str = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", model_str).strip()
        code_str = str(r[2] or "").strip()
        gen_str = str(r[3] or "").strip()
        series_str = str(r[6] or "").strip()
        yr_val = None
        try:
            m_yr = re.search(r"(19\d\d|20\d\d)", str(r[7] or ""))
            if m_yr:
                yr_val = int(m_yr.group(1))
        except Exception:
            pass
        if not yr_val:
            yr_val = 2022

        msrp_raw = str(r[9] or "")
        msrp_idr = 0.0
        m_rp = re.search(r"Rp\s*([\d\.,]+)", msrp_raw)
        if m_rp:
            digits = re.sub(r"[^\d]", "", m_rp.group(1))
            if digits:
                msrp_idr = float(digits)

        cpu_str = str(r[10] or "-").strip()
        gpu_str = str(r[11] or "-").strip()
        ram_str = str(r[12] or "").strip()
        ram_gb = 8
        m_ram = re.search(r"(\d{1,3})\s*GB", ram_str, re.I)
        if m_ram:
            ram_gb = int(m_ram.group(1))

        sto_str = str(r[13] or "").strip()
        sto_gb = 512
        m_sto = re.search(r"(\d{1,4})\s*(?:GB|TB)", sto_str, re.I)
        if m_sto:
            val_s = int(m_sto.group(1))
            sto_gb = val_s * 1024 if "tb" in sto_str.lower() else val_s

        lyr_str = str(r[16] or "").strip()
        lyr_inch = None
        m_inch = re.search(r"(\d{1,2}(?:\.\d)?)\s*[\"']?", lyr_str)
        if m_inch:
            lyr_inch = float(m_inch.group(1))

        hz_val = 60
        m_hz = re.search(r"(\d{2,3})\s*Hz", str(r[18] or ""), re.I)
        if m_hz:
            hz_val = int(m_hz.group(1))

        bat_wh = None
        m_wh = re.search(r"(\d{2,3}(?:\.\d)?)\s*Wh", str(r[19] or ""), re.I)
        if m_wh:
            bat_wh = int(round(float(m_wh.group(1))))

        w_kg = None
        m_kg = re.search(r"(\d{1,2}(?:\.\d+)?)\s*kg", str(r[21] or ""), re.I)
        if m_kg:
            w_kg = float(m_kg.group(1))

        disp_type = str(r[15] or "-").strip()
        res_str = str(r[17] or "-").strip()
        mat_bodi = str(r[20] or "-").strip()
        os_awal = str(r[22] or "-").strip()

        p_brand = "Intel" if "intel" in cpu_str.lower() else ("AMD" if "amd" in cpu_str.lower() or "ryzen" in cpu_str.lower() else ("Apple" if "apple" in cpu_str.lower() or "m1" in cpu_str.lower() or "m2" in cpu_str.lower() or "m3" in cpu_str.lower() else "Qualcomm"))
        g_brand = "NVIDIA" if any(k in gpu_str.lower() for k in ["geforce", "rtx", "gtx", "quadro"]) else ("AMD" if "radeon" in gpu_str.lower() else ("Intel" if any(k in gpu_str.lower() for k in ["intel", "iris", "uhd", "arc"]) else "Apple"))
        vram_gb = 0
        m_vr = re.search(r"(\d{1,2})\s*GB", gpu_str, re.I)
        if m_vr and g_brand in ("NVIDIA", "AMD"):
            vram_gb = int(m_vr.group(1))

        c_norm = re.sub(r"[^a-zA-Z0-9]", "", code_str).upper()
        mk_key = f"{brand_str.lower()} {model_str.lower()}"

        fair_market_val = None
        if c_norm and c_norm in olx_by_code:
            fair_market_val = float(olx_by_code[c_norm])
        elif mk_key in olx_by_mk:
            fair_market_val = float(olx_by_mk[mk_key])
        else:
            fair_market_val = calculate_econometric_fmv(
                brand=brand_str,
                model=model_str,
                cpu=cpu_str,
                gpu=gpu_str,
                ram_gb=ram_gb,
                storage_gb=sto_gb,
                release_year=yr_val,
                msrp_idr=msrp_idr
            )

        b_id = get_or_create_brand_id(brand_str)
        model_lookup_key = (b_id, model_str.lower(), c_norm)

        if model_lookup_key in existing_models:
            m_id = existing_models[model_lookup_key]
            target_cur.execute(
                "UPDATE master_models SET fair_market_value = ? WHERE id = ?",
                (fair_market_val, m_id)
            )
            target_cur.execute(
                "UPDATE master_variants SET fair_market_value = ? WHERE model_id = ?",
                (fair_market_val, m_id)
            )
            updated_models_count += 1
        else:
            target_cur.execute("""
                INSERT INTO master_models (
                    brand_id, name, series, chassis_code, generation, release_year,
                    processor_brand, processor_model, gpu_brand, gpu_model, vram_gb, tgp_watt,
                    display_type, screen_size_inch, refresh_rate_hz, resolution,
                    battery_wh, weight_kg, chassis_material, os_at_launch, created_at, fair_market_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                b_id, model_str, series_str, code_str, gen_str, yr_val,
                p_brand, cpu_str, g_brand, gpu_str, vram_gb, 0,
                disp_type, lyr_inch, hz_val, res_str,
                bat_wh, w_kg, mat_bodi, os_awal, now_str, fair_market_val
            ))
            new_m_id = target_cur.lastrowid
            existing_models[model_lookup_key] = new_m_id
            new_models_count += 1

            v_name = f"{model_str} {cpu_str[:22]} {ram_gb}GB/{sto_gb}GB".strip()
            target_cur.execute("""
                INSERT INTO master_variants (
                    model_id, variant_name, ram_gb, storage_gb, official_msrp_new, fair_market_value, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                new_m_id, v_name, ram_gb, sto_gb, msrp_idr if msrp_idr > 0 else 8999000, fair_market_val, now_str
            ))

    target_cur.execute("SELECT id, name, release_year, processor_model, gpu_model FROM master_models WHERE fair_market_value IS NULL OR fair_market_value = 0")
    old_unpriced = target_cur.fetchall()
    for row in old_unpriced:
        m_id, m_name, m_yr, m_cpu, m_gpu = row
        target_cur.execute("SELECT official_msrp_new, ram_gb, storage_gb FROM master_variants WHERE model_id = ?", (m_id,))
        var_row = target_cur.fetchone()
        msrp_val = float(var_row[0]) if var_row and var_row[0] else 12999000
        r_gb = var_row[1] if var_row else 16
        s_gb = var_row[2] if var_row else 512
        calculated_fmv = calculate_econometric_fmv("Laptop", m_name, m_cpu or "", m_gpu or "", r_gb, s_gb, m_yr, msrp_val)
        target_cur.execute("UPDATE master_models SET fair_market_value = ? WHERE id = ?", (calculated_fmv, m_id))
        target_cur.execute("UPDATE master_variants SET fair_market_value = ? WHERE model_id = ?", (calculated_fmv, m_id))

    # Pembersihan final: pastikan seluruh model di master_models bebas dari akhiran redundan (YYYY)
    target_cur.execute("SELECT id, name FROM master_models")
    for m_id, m_name in target_cur.fetchall():
        if re.search(r"\s*\((?:19\d\d|20\d\d)\)$", m_name):
            cleaned = re.sub(r"\s*\((?:19\d\d|20\d\d)\)$", "", m_name).strip()
            target_cur.execute("UPDATE master_models SET name = ? WHERE id = ?", (cleaned, m_id))
            target_cur.execute("SELECT id, variant_name FROM master_variants WHERE model_id = ?", (m_id,))
            for vid, vname in target_cur.fetchall():
                v_cleaned = re.sub(r"\s*\((?:19\d\d|20\d\d)\)", "", vname).strip()
                target_cur.execute("UPDATE master_variants SET variant_name = ? WHERE id = ?", (v_cleaned, vid))

    target_conn.commit()
    src_conn.close()
    print(f"[SYNC SELESAI] Model Baru Disinkronkan: {new_models_count:,} | Model Diperbarui FMV: {updated_models_count:,}")


def main():
    print("=" * 70)
    print("SINKRONISASI DATABASE MASTER KATALOG & KALKULASI FAIR MARKET VALUE OLX")
    print("=" * 70)
    if not TARGET_DB_PATH.exists():
        print(f"[ERROR] Database target {TARGET_DB_PATH} tidak ditemukan.")
        return 1

    conn = sqlite3.connect(str(TARGET_DB_PATH))
    try:
        ensure_schema_migrations(conn)
        olx_codes, olx_mks = load_olx_fair_values()
        sync_kode_model_lookup(conn)
        sync_master_models_and_variants(conn, olx_codes, olx_mks)

        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM master_brands")
        b_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM master_models")
        m_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM master_variants")
        v_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM kode_model_lookup")
        k_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(*), avg(fair_market_value) FROM master_models WHERE fair_market_value > 0")
        fmv_row = cur.fetchone()

        print("\n" + "=" * 70)
        print("RINGKASAN STATUS DATABASE SETELAH SINKRONISASI:")
        print(f"- Total Brand Master      : {b_cnt:,} brand")
        print(f"- Total Model Master      : {m_cnt:,} model")
        print(f"- Total Varian Master     : {v_cnt:,} varian")
        print(f"- Total Indeks Kode Sasis : {k_cnt:,} nomor sasis")
        print(f"- Model dengan FMV OLX    : {fmv_row[0]:,} dari {m_cnt:,} model ({fmv_row[0]/m_cnt*100:.1f}%)")
        print(f"- Rata-Rata FMV Bekas     : Rp {fmv_row[1]:,.0f}")
        print("=" * 70)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
